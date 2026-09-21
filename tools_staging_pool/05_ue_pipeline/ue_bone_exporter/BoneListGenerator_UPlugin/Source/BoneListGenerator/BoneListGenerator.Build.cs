using UnrealBuildTool;

public class BoneListGenerator : ModuleRules
{
	public BoneListGenerator(ReadOnlyTargetRules Target) : base(Target)
	{
		PCHUsage = ModuleRules.PCHUsageMode.UseExplicitOrSharedPCHs;

		PublicDependencyModuleNames.AddRange(
			new string[]
			{
				"Core",
			}
		);

		PrivateDependencyModuleNames.AddRange(
			new string[]
			{
				"CoreUObject",
				"Engine",
				"Slate",
				"SlateCore",
				"UnrealEd",
				"ContentBrowser",
				"AssetTools",
				"ToolMenus",
				"EditorStyle",
				"DesktopPlatform"
			}
		);
	}
}
