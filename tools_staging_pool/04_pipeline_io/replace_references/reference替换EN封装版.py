import maya.cmds as cmds
import os

def replace_references_with_new_file_ui(selected_references, new_file_path):
    """
    Replace multiple selected reference files and rename namespaces.
    
    :param selected_references: List of selected reference nodes in the Outliner view.
    :param new_file_path: Path to the new file to replace references with.
    """
    def rename_namespace(node, new_namespace):
        """
        Rename a namespace, add a suffix if the namespace already exists.

        :param node: The reference node name.
        :param new_namespace: The new namespace name.
        """
        index = 1
        original_namespace = new_namespace
        while cmds.namespace(exists=new_namespace):
            new_namespace = "{}{}".format(original_namespace, index)
            index += 1
        # Remove "RN" from the namespace name
        new_namespace = new_namespace.replace("RN", "")
        # Remove "RN" from the node name
        node = node.replace("RN", "")
        cmds.namespace(rename=[node, new_namespace])

    for reference in selected_references:
        # Load the new file and replace the old reference
        cmds.file(new_file_path, loadReference=reference)

        # Get the file name of the new file as the new namespace
        new_namespace = os.path.splitext(os.path.basename(new_file_path))[0]

        # Rename the new namespace
        rename_namespace(reference, new_namespace)

def replace_references_in_maya():
    """
    Create a UI for selecting reference files to replace in Maya.
    """
    if cmds.window("replaceReferenceWindow", exists=True):
        cmds.deleteUI("replaceReferenceWindow", window=True)

    window = cmds.window("replaceReferenceWindow", title="Replace Reference Files", widthHeight=(300, 100))
    cmds.columnLayout(adjustableColumn=True)
    cmds.text(label="Select reference files to replace in the Outliner view:")
    cmds.button(label="Select New File and Replace References", command=replace_references_from_ui)
    cmds.showWindow(window)

def replace_references_from_ui(*args):
    # Get selected reference nodes
    selected_nodes = cmds.ls(selection=True)
    selected_references = []

    for node in selected_nodes:
        reference_node = cmds.referenceQuery(node, referenceNode=True)
        if reference_node and reference_node not in selected_references:
            selected_references.append(reference_node)

    if not selected_references:
        cmds.warning("No old references selected. Please select references to replace in the Outliner view.")
        return

    # Open a file dialog to choose the new file
    new_file_path = cmds.fileDialog2(fileMode=1, caption="Select the new file")
    if not new_file_path:
        return

    # Call the function to replace the selected references
    replace_references_with_new_file_ui(selected_references, new_file_path[0])

if __name__ == "__main__":
    replace_references_in_maya()
