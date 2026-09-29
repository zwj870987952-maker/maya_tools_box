//Maya ASCII 2023 scene
//Name: Roadstones_1_1.ma
//Last modified: Mon, Aug 01, 2022 04:25:11 PM
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
fileInfo "UUID" "5404CDE0-4BDC-3BE3-6786-55935638A42E";
createNode transform -n "Roadstones_1_1";
	rename -uid "1F7FE5FA-4917-6229-76A2-33ADDBD3408F";
	setAttr ".t" -type "double3" -586.809814453125 0.14993000030517578 -246.97705078125 ;
	setAttr ".rp" -type "double3" 586.809814453125 -0.14993000030517578 246.97705078125 ;
	setAttr ".sp" -type "double3" 586.809814453125 -0.14993000030517578 246.97705078125 ;
createNode mesh -n "Roadstones_1_1Shape" -p "Roadstones_1_1";
	rename -uid "2B0C5C2E-4A8B-A68D-012D-7ABC1781991F";
	setAttr -k off ".v";
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".uvst[0].uvsn" -type "string" "map1";
	setAttr -s 64 ".uvst[0].uvsp[0:63]" -type "float2" 0.67510003 0.72659999
		 0.676 0.72659999 0.67640001 0.82609999 0.67559999 0.82609999 0.67580003 0.81470001
		 0.6807 0.81470001 0.68000001 0.81470001 0.67659998 0.81470001 0.6814 0.72659999 0.68059999
		 0.72659999 0.68019998 0.82630002 0.68089998 0.82630002 0.67629999 0.72659999 0.6803
		 0.72659999 0.68000001 0.82480001 0.67659998 0.82480001 0.67510003 0.78479999 0.67500001
		 0.79290003 0.6814 0.78479999 0.68150002 0.79210001 0.68129998 0.78479999 0.67559999
		 0.88429999 0.67580003 0.90109998 0.68089998 0.88450003 0.6807 0.90109998 0.68019998
		 0.88450003 0.68000001 0.8829 0.68000001 0.90109998 0.67659998 0.8829 0.67640001 0.88429999
		 0.67659998 0.90109998 0.67629999 0.78479999 0.676 0.78479999 0.6803 0.78479999 0.68059999
		 0.78479999 0.676 0.72659999 0.67510003 0.72659999 0.67559999 0.82609999 0.67640001
		 0.82609999 0.67659998 0.81470001 0.68000001 0.81470001 0.68059999 0.72659999 0.6814
		 0.72659999 0.68089998 0.82630002 0.68019998 0.82630002 0.6803 0.72659999 0.67629999
		 0.72659999 0.67659998 0.82480001 0.68000001 0.82480001 0.67510003 0.78479999 0.67559999
		 0.88429999 0.68089998 0.88450003 0.68019998 0.88450003 0.68000001 0.90109998 0.68000001
		 0.8829 0.67640001 0.88429999 0.67659998 0.8829 0.67659998 0.90109998 0.67510003 0.78479999
		 0.67629999 0.78479999 0.676 0.78479999 0.6814 0.78479999 0.6803 0.78479999 0.68059999
		 0.78479999;
	setAttr ".cuvs" -type "string" "map1";
	setAttr ".dcc" -type "string" "Ambient+Diffuse";
	setAttr -s 32 ".vt[0:31]"  586.55859375 -0.14993 240.50341797 584.0078125 -0.14993 242.41479492
		 584.47558594 1.39130878 243.099609375 586.55859375 1.39130878 241.53881836 589.61181641 -0.14993 242.41479492
		 587.061035156 -0.14993 240.50341797 587.061035156 1.39130878 241.53881836 589.14404297 1.39130878 243.099609375
		 586.81005859 1.65182018 241.89501953 586.81005859 1.65182018 252.080566406 589.40820313 1.65182018 250.61474609
		 589.013671875 1.65182018 243.54663086 584.60595703 1.65182018 243.54663086 584.21142578 1.65182018 250.61474609
		 587.077148438 -0.14991999 253.45068359 590.092773438 -0.14991999 251.74975586 589.54638672 1.3949995 251.044921875
		 587.077148438 1.3949995 252.43774414 583.52685547 -0.14991999 251.74975586 586.54248047 -0.14991999 253.45068359
		 586.54248047 1.3949995 252.43774414 584.073242188 1.3949995 251.044921875 583.75341797 -0.14993 242.91088867
		 583.28662109 -0.14991999 251.2800293 583.82470703 1.37077999 250.58618164 584.21484375 1.37077999 243.58642578
		 590.33300781 -0.14991999 251.2800293 589.86621094 -0.14993 242.91088867 589.40478516 1.37077999 243.58642578
		 589.79492188 1.37077999 250.58618164 586.81005859 -0.14993 240.61108398 586.81005859 -0.14991999 253.3059082;
	setAttr -s 59 ".ed[0:58]"  0 1 0 1 2 1 2 3 0 3 0 0 4 5 0 5 6 0 6 7 0
		 7 4 1 8 9 1 9 10 0 10 11 0 11 8 0 12 13 0 13 9 0 8 12 0 14 15 0 15 16 1 16 17 0 17 14 1
		 18 19 0 19 20 1 20 21 0 21 18 1 22 23 0 23 24 1 24 25 0 25 22 1 26 27 0 27 28 1 28 29 0
		 29 26 1 0 5 0 5 30 0 30 0 0 14 19 0 19 31 0 31 14 0 3 8 1 8 6 1 6 3 1 17 9 1 9 20 1
		 20 17 1 16 29 1 29 10 1 10 16 1 28 7 1 7 11 1 11 28 1 21 13 1 13 24 1 24 21 1 2 25 1
		 25 12 1 12 2 1 27 4 0 1 22 0 15 26 0 23 18 0;
	setAttr -s 46 ".n[0:45]" -type "float3"  1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20;
	setAttr -s 28 -ch 104 ".fc[0:27]" -type "polyFaces" 
		f 4 0 1 2 3
		mu 0 4 0 1 2 3
		f 4 4 5 6 7
		mu 0 4 35 36 37 38
		f 4 8 9 10 11
		mu 0 4 4 5 6 7
		f 4 12 13 -9 14
		mu 0 4 39 40 5 4
		f 4 15 16 17 18
		mu 0 4 8 9 10 11
		f 4 19 20 21 22
		mu 0 4 41 42 43 44
		f 4 23 24 25 26
		mu 0 4 12 13 14 15
		f 4 27 28 29 30
		mu 0 4 45 46 47 48
		f 3 31 32 33
		mu 0 3 16 17 49
		f 3 34 35 36
		mu 0 3 18 19 20
		f 3 37 38 39
		mu 0 3 21 22 50
		f 3 40 41 42
		mu 0 3 23 24 51
		f 3 43 44 45
		mu 0 3 25 26 27
		f 3 46 47 48
		mu 0 3 28 29 30
		f 3 49 50 51
		mu 0 3 52 53 54
		f 3 52 53 54
		mu 0 3 55 56 57
		f 4 -15 -38 -3 -55
		mu 0 4 57 22 21 55
		f 4 -10 -41 -18 -46
		mu 0 4 27 24 23 25
		f 4 -11 -45 -30 -49
		mu 0 4 30 27 26 28
		f 4 -14 -50 -22 -42
		mu 0 4 24 53 52 51
		f 4 -13 -54 -26 -51
		mu 0 4 53 57 56 54
		f 4 -12 -48 -7 -39
		mu 0 4 22 30 29 50
		f 4 -4 -40 -6 -32
		mu 0 4 16 21 50 58
		f 4 -29 55 -8 -47
		mu 0 4 28 31 32 29
		f 4 -27 -53 -2 56
		mu 0 4 59 56 55 60
		f 4 -31 -44 -17 57
		mu 0 4 33 26 25 34
		f 4 -21 -35 -19 -43
		mu 0 4 51 61 18 23
		f 4 -25 58 -23 -52
		mu 0 4 54 62 63 52;
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
connectAttr "Roadstones_1_1Shape.iog" "aiStandardSurface1SG.dsm" -na;
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
// End of Roadstones_1_1.ma
