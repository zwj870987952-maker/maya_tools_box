//Maya ASCII 2023 scene
//Name: Rock_3_5.ma
//Last modified: Mon, Aug 01, 2022 04:22:31 PM
//Codeset: 1252
requires maya "2023";
requires -nodeType "aiStandardSurface" "mtoa" "5.1.0";
requires "stereoCamera" "10.0";
currentUnit -l centimeter -a degree -t film;
fileInfo "application" "maya";
fileInfo "product" "Maya 2023";
fileInfo "version" "2023";
fileInfo "cutIdentifier" "202202161415-df43006fd3";
fileInfo "osv" "Windows 10 Home v2009 (Build: 19044)";
fileInfo "UUID" "E0CD8BDA-46B8-F994-3605-CDB5A69A590C";
createNode transform -n "Rock_3_5";
	rename -uid "6063F241-436B-016D-26F5-9CA954A7D3E0";
	setAttr ".t" -type "double3" -660.07958984375 0.78439998626708984 -322.834228515625 ;
	setAttr ".rp" -type "double3" 660.07958984375 -0.78439998626708984 322.834228515625 ;
	setAttr ".sp" -type "double3" 660.07958984375 -0.78439998626708984 322.834228515625 ;
createNode mesh -n "Rock_3_5Shape" -p "Rock_3_5";
	rename -uid "1F1E7CFC-4685-2FDB-4976-32A7DDBCB5AE";
	setAttr -k off ".v";
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".uvst[0].uvsn" -type "string" "map1";
	setAttr -s 50 ".uvst[0].uvsp[0:49]" -type "float2" 0.62339997 0.68599999
		 0.6232 0.68599999 0.62360001 0.79470003 0.62370002 0.8003 0.62330002 0.68599999 0.62580001
		 0.68599999 0.62529999 0.87559998 0.62370002 0.79960001 0.62510002 0.84689999 0.62379998
		 0.78659999 0.62529999 0.85750002 0.62599999 0.89139998 0.62730002 0.68599999 0.6257
		 0.68599999 0.62519997 0.86879998 0.62620002 0.91360003 0.62599999 0.68599999 0.62620002
		 0.91390002 0.62550002 0.88120002 0.62370002 0.78100002 0.62459999 0.8653 0.62459999
		 0.86320001 0.62459999 0.87129998 0.62449998 0.86059999 0.62459999 0.86290002 0.62459999
		 0.86860001 0.62489998 0.89270002 0.62489998 0.89969999 0.62489998 0.89539999 0.625
		 0.89859998 0.625 0.90130001 0.625 0.90469998 0.62519997 0.91649997 0.62510002 0.9206
		 0.62519997 0.91659999 0.62449998 0.80940002 0.62540001 0.80940002 0.62510002 0.80940002
		 0.625 0.80940002 0.62550002 0.68599999 0.62349999 0.68599999 0.62379998 0.80479997
		 0.625 0.86290002 0.62730002 0.68599999 0.62449998 0.80940002 0.62449998 0.80940002
		 0.62449998 0.80940002 0.62540001 0.80940002 0.62510002 0.80940002 0.62510002 0.80940002;
	setAttr ".cuvs" -type "string" "map1";
	setAttr ".dcc" -type "string" "Ambient+Diffuse";
	setAttr -s 25 ".vt[0:24]"  652.64648438 -0.78439999 319.28491211 651.86279297 -0.78439999 328.71948242
		 653.16064453 2.25127029 326.78466797 653.66650391 2.4063797 320.72216797 652.21875 -0.78439999 329.31323242
		 662.3984375 -0.78439999 332.31542969 660.32373047 4.4992485 329.44702148 653.53759766 2.40353012 327.3762207
		 659.33740234 4.56977081 317.40454102 654.098632813 2.885149 320.82763672 660.25830078 4.86592102 328.98217773
		 663.19873047 5.81148148 323.38989258 668.28955078 -0.78439999 323.17260742 661.89794922 -0.78439999 313.43994141
		 659.79980469 4.32709122 316.9362793 663.7109375 5.56388092 323.094482422 663.054199219 -0.78439999 332.094970703
		 668.29638672 -0.78439999 323.88989258 663.74121094 5.5765686 323.79394531 660.90625 4.66590881 329.19799805
		 653.61279297 2.72887039 326.81982422 654.043945313 2.53879929 320.076171875 659.20996094 4.14770126 316.8034668
		 653.023925781 -0.78439999 318.63110352 661.25341797 -0.78439999 313.35302734;
	setAttr -s 46 ".ed[0:45]"  0 1 0 1 2 0 2 3 1 3 0 1 4 5 0 5 6 0 6 7 1
		 7 4 0 8 9 1 9 10 1 10 11 0 11 8 0 12 13 0 13 14 0 14 15 0 15 12 1 16 17 0 17 18 1
		 18 19 0 19 16 0 9 20 1 20 10 0 21 3 1 3 9 1 9 21 1 2 7 1 7 20 1 20 2 1 22 8 1 8 14 1
		 14 22 1 6 19 1 19 10 1 10 6 1 15 11 1 11 18 1 18 15 1 22 21 0 1 4 0 21 23 1 23 0 0
		 17 12 0 5 16 0 13 24 0 24 22 0 24 23 0;
	setAttr -s 36 ".n[0:35]" -type "float3"  1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20;
	setAttr -s 22 -ch 82 ".fc[0:21]" -type "polyFaces" 
		f 4 0 1 2 3
		mu 0 4 0 1 2 3
		f 4 4 5 6 7
		mu 0 4 4 5 6 7
		f 4 8 9 10 11
		mu 0 4 8 9 10 11
		f 4 12 13 14 15
		mu 0 4 12 13 14 15
		f 4 16 17 18 19
		mu 0 4 16 43 17 18
		f 3 20 21 -10
		mu 0 3 9 19 10
		f 3 22 23 24
		mu 0 3 20 21 22
		f 3 25 26 27
		mu 0 3 23 24 25
		f 3 28 29 30
		mu 0 3 26 27 28
		f 3 31 32 33
		mu 0 3 29 30 31
		f 3 34 35 36
		mu 0 3 32 33 34
		f 4 37 -25 -9 -29
		mu 0 4 26 20 22 27
		f 4 -3 -28 -21 -24
		mu 0 4 21 23 25 22
		f 4 -7 -34 -22 -27
		mu 0 4 24 29 31 25
		f 4 -15 -30 -12 -35
		mu 0 4 32 28 27 33
		f 4 -19 -36 -11 -33
		mu 0 4 30 34 33 31
		f 4 -8 -26 -2 38
		mu 0 4 35 24 23 44
		f 4 39 40 -4 -23
		mu 0 4 20 45 46 21
		f 4 -16 -37 -18 41
		mu 0 4 36 32 34 47
		f 4 -6 42 -20 -32
		mu 0 4 29 37 48 30
		f 4 -14 43 44 -31
		mu 0 4 28 49 38 26
		f 4 45 -40 -38 -45
		mu 0 4 39 40 41 42;
	setAttr ".cd" -type "dataPolyComponent" Index_Data Edge 0 ;
	setAttr ".cvd" -type "dataPolyComponent" Index_Data Vertex 0 ;
	setAttr ".pd[0]" -type "dataPolyComponent" Index_Data UV 0 ;
	setAttr ".hfd" -type "dataPolyComponent" Index_Data Face 0 ;
	setAttr ".db" yes;
	setAttr ".de" 1;
	setAttr ".bw" 5;
createNode materialInfo -n "materialInfo1";
	rename -uid "2525C32B-4C69-91A2-4C1D-41BDFC460F88";
createNode shadingEngine -n "aiStandardSurface1SG";
	rename -uid "8472593A-4BE3-7326-2990-7BB44705F98A";
	setAttr ".ihi" 0;
	setAttr -s 355 ".dsm";
	setAttr ".ro" yes;
createNode aiStandardSurface -n "Toon_shd";
	rename -uid "466C0731-4F60-BED2-D82C-D28AF0D43EBA";
	setAttr ".base" 0;
	setAttr ".subsurface" 1;
	setAttr ".subsurface_scale" 0.5;
	setAttr ".subsurface_type" 2;
	setAttr ".sheen_color" -type "float3" 0.22946176 0.22946176 0.22946176 ;
	setAttr ".sheen_roughness" 0.27762040495872498;
	setAttr ".coat_roughness" 0.26865673065185547;
	setAttr ".coat_IOR" 1.5315315723419189;
	setAttr ".emission" 1;
	setAttr ".emission_color" -type "float3" 0 0 0 ;
createNode file -n "file1";
	rename -uid "3486876B-4D3F-23F8-57CB-FDABC798AFE8";
	setAttr ".ftn" -type "string" "C:/Users/chauliac/Dropbox/WZX/Works In Progress/AssetIt/00_Ressources/RESSOURCES/Medieval Toon/textures/Gradient-F.png";
	setAttr ".cs" -type "string" "Raw";
createNode place2dTexture -n "place2dTexture1";
	rename -uid "78B6D35C-41B7-6D51-D8E0-07964DD1A7A1";
createNode lightLinker -s -n "lightLinker1";
	rename -uid "2940B33D-4B53-4605-2C66-069D7C9025F8";
	setAttr -s 4 ".lnk";
	setAttr -s 4 ".slnk";
select -ne :time1;
	setAttr ".o" 0;
select -ne :hardwareRenderingGlobals;
	setAttr ".otfna" -type "stringArray" 22 "NURBS Curves" "NURBS Surfaces" "Polygons" "Subdiv Surface" "Particles" "Particle Instance" "Fluids" "Strokes" "Image Planes" "UI" "Lights" "Cameras" "Locators" "Joints" "IK Handles" "Deformers" "Motion Trails" "Components" "Hair Systems" "Follicles" "Misc. UI" "Ornaments"  ;
	setAttr ".otfva" -type "Int32Array" 22 0 1 1 1 1 1
		 1 1 1 0 0 0 0 0 0 0 0 0
		 0 0 0 0 ;
	setAttr ".mhl" 10;
	setAttr ".hwi" yes;
	setAttr ".msaa" yes;
	setAttr ".aasc" 4;
	setAttr ".laa" yes;
	setAttr ".fprt" yes;
select -ne :renderPartition;
	setAttr -s 4 ".st";
select -ne :renderGlobalsList1;
select -ne :defaultShaderList1;
	setAttr -s 9 ".s";
select -ne :postProcessList1;
	setAttr -s 2 ".p";
select -ne :defaultRenderUtilityList1;
	setAttr -s 4 ".u";
select -ne :defaultRenderingList1;
select -ne :lightList1;
	setAttr -s 3 ".l";
select -ne :defaultTextureList1;
	setAttr -s 4 ".tx";
select -ne :lambert1;
	setAttr ".c" -type "float3" 0.40509915 0.40509915 0.40509915 ;
select -ne :standardSurface1;
	setAttr ".b" 0.80000001192092896;
	setAttr ".bc" -type "float3" 1 1 1 ;
	setAttr ".s" 0.20000000298023224;
select -ne :initialShadingGroup;
	setAttr ".ro" yes;
select -ne :initialParticleSE;
	setAttr ".ro" yes;
select -ne :defaultRenderGlobals;
	addAttr -ci true -h true -sn "dss" -ln "defaultSurfaceShader" -dt "string";
	setAttr ".ren" -type "string" "arnold";
	setAttr ".outf" 51;
	setAttr ".imfkey" -type "string" "exr";
	setAttr ".ifp" -type "string" "None";
	setAttr ".dss" -type "string" "lambert1";
select -ne :defaultResolution;
	setAttr ".w" 2048;
	setAttr ".h" 2048;
	setAttr ".pa" 1;
	setAttr ".dar" 1;
select -ne :defaultLightSet;
	setAttr -s 3 ".dsm";
select -ne :defaultColorMgtGlobals;
	setAttr ".cfe" yes;
	setAttr ".cfp" -type "string" "<MAYA_RESOURCES>/OCIO-configs/Maya2022-default/config.ocio";
	setAttr ".vtn" -type "string" "ACES 1.0 SDR-video (sRGB)";
	setAttr ".vn" -type "string" "ACES 1.0 SDR-video";
	setAttr ".dn" -type "string" "sRGB";
	setAttr ".wsn" -type "string" "ACEScg";
	setAttr ".otn" -type "string" "ACES 1.0 SDR-video (sRGB)";
	setAttr ".potn" -type "string" "ACES 1.0 SDR-video (sRGB)";
select -ne :hardwareRenderGlobals;
	setAttr ".ctrs" 256;
	setAttr ".btrs" 512;
connectAttr "aiStandardSurface1SG.msg" "materialInfo1.sg";
connectAttr "Toon_shd.msg" "materialInfo1.m";
connectAttr "Toon_shd.msg" "materialInfo1.t" -na;
connectAttr "Toon_shd.out" "aiStandardSurface1SG.ss";
connectAttr "Rock_3_5Shape.iog" "aiStandardSurface1SG.dsm" -na;
connectAttr "file1.oc" "Toon_shd.base_color";
connectAttr "file1.oc" "Toon_shd.subsurface_color";
connectAttr ":defaultColorMgtGlobals.cme" "file1.cme";
connectAttr ":defaultColorMgtGlobals.cfe" "file1.cmcf";
connectAttr ":defaultColorMgtGlobals.cfp" "file1.cmcp";
connectAttr ":defaultColorMgtGlobals.wsn" "file1.ws";
connectAttr "place2dTexture1.c" "file1.c";
connectAttr "place2dTexture1.tf" "file1.tf";
connectAttr "place2dTexture1.rf" "file1.rf";
connectAttr "place2dTexture1.mu" "file1.mu";
connectAttr "place2dTexture1.mv" "file1.mv";
connectAttr "place2dTexture1.s" "file1.s";
connectAttr "place2dTexture1.wu" "file1.wu";
connectAttr "place2dTexture1.wv" "file1.wv";
connectAttr "place2dTexture1.re" "file1.re";
connectAttr "place2dTexture1.of" "file1.of";
connectAttr "place2dTexture1.r" "file1.ro";
connectAttr "place2dTexture1.n" "file1.n";
connectAttr "place2dTexture1.vt1" "file1.vt1";
connectAttr "place2dTexture1.vt2" "file1.vt2";
connectAttr "place2dTexture1.vt3" "file1.vt3";
connectAttr "place2dTexture1.vc1" "file1.vc1";
connectAttr "place2dTexture1.o" "file1.uv";
connectAttr "place2dTexture1.ofs" "file1.fs";
relationship "link" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" "aiStandardSurface1SG.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" "aiStandardSurface1SG.message" ":defaultLightSet.message";
connectAttr "aiStandardSurface1SG.pa" ":renderPartition.st" -na;
connectAttr "Toon_shd.msg" ":defaultShaderList1.s" -na;
connectAttr "place2dTexture1.msg" ":defaultRenderUtilityList1.u" -na;
connectAttr "file1.msg" ":defaultTextureList1.tx" -na;
// End of Rock_3_5.ma
