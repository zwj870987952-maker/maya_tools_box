//Maya ASCII 2023 scene
//Name: Roadstones_1_4.ma
//Last modified: Mon, Aug 01, 2022 04:24:28 PM
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
fileInfo "UUID" "2FFF725D-4216-C896-2C8D-DFBEE8CDCACD";
createNode transform -n "Roadstones_1_4";
	rename -uid "2A2E3A4D-40A9-4CE9-213B-5BB33DCA1E92";
	setAttr ".t" -type "double3" -600.644775390625 0.14993000030517578 -277.1927490234375 ;
	setAttr ".rp" -type "double3" 600.644775390625 -0.14993000030517578 277.1927490234375 ;
	setAttr ".sp" -type "double3" 600.644775390625 -0.14993000030517578 277.1927490234375 ;
createNode mesh -n "Roadstones_1_4Shape" -p "Roadstones_1_4";
	rename -uid "6D2C09C6-466E-AF90-9C9C-BB8B36C25164";
	setAttr -k off ".v";
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".uvst[0].uvsn" -type "string" "map1";
	setAttr -s 57 ".uvst[0].uvsp[0:56]" -type "float2" 0.67989999 0.72659999
		 0.6796 0.82480001 0.67680001 0.72659999 0.67790002 0.72659999 0.67790002 0.82609999
		 0.67699999 0.82609999 0.67809999 0.81470001 0.67940003 0.81470001 0.67839998 0.81470001
		 0.67809999 0.72659999 0.67970002 0.72659999 0.67949998 0.82599998 0.67820001 0.82599998
		 0.6771 0.81470001 0.67839998 0.72659999 0.6771 0.82599998 0.67839998 0.82599998 0.67809999
		 0.78479999 0.67790002 0.79000002 0.67799997 0.78479999 0.67690003 0.8829 0.67699999
		 0.88419998 0.6771 0.90109998 0.67949998 0.88410002 0.6796 0.8829 0.67940003 0.90109998
		 0.6771 0.88410002 0.67820001 0.88410002 0.67809999 0.90109998 0.67790002 0.88419998
		 0.67839998 0.88410002 0.67839998 0.90109998 0.67790002 0.78479999 0.6767 0.78479999
		 0.67680001 0.78479999 0.67989999 0.78479999 0.67970002 0.78479999 0.6767 0.72659999
		 0.67690003 0.82480001 0.67989999 0.72659999 0.6796 0.82480001 0.67940003 0.81470001
		 0.6771 0.81470001 0.67680001 0.72659999 0.67970002 0.72659999 0.67949998 0.82599998
		 0.67690003 0.8829 0.6771 0.90109998 0.6796 0.8829 0.67949998 0.88410002 0.67940003
		 0.90109998 0.67680001 0.78479999 0.6767 0.78479999 0.67989999 0.78479999 0.67970002
		 0.78479999 0.6767 0.72659999 0.67690003 0.82480001;
	setAttr ".cuvs" -type "string" "map1";
	setAttr ".dcc" -type "string" "Ambient+Diffuse";
	setAttr -s 29 ".vt[0:28]"  603.9296875 -0.14991999 281.19702148 603.9296875 -0.14993 272.76879883
		 603.42480469 1.37112999 273.47485352 603.42480469 1.37112999 280.52441406 597.63232422 -0.14991999 281.63793945
		 599.82226563 -0.14991999 282.60375977 599.90039063 1.39109039 281.73657227 598.13183594 1.39109039 280.95629883
		 600.21435547 1.65182018 281.39575195 603.035644531 1.65182018 280.50708008 603.035644531 1.65182018 273.51928711
		 600.91455078 1.65182018 273.014648438 600.38330078 -0.14991999 282.63427734 603.64404297 -0.14991999 281.60766602
		 603.1328125 1.38957977 280.92700195 600.46191406 1.38957977 281.76782227 598.24023438 1.65182018 280.52490234
		 598.24023438 1.65182018 273.52294922 601.013183594 -0.14993 271.7512207 597.65673828 -0.14993 272.38916016
		 598.15625 1.38967037 273.10375977 600.95068359 1.3896904 272.57275391 603.63671875 -0.14993 272.37573242
		 603.12548828 1.38971996 273.090576172 600.12060547 -0.14991999 282.42993164 597.85302734 1.37049007 280.5246582
		 597.85302734 1.37049007 273.47460938 597.35986328 -0.14991999 281.19702148 597.35986328 -0.14993 272.76879883;
	setAttr -s 53 ".ed[0:52]"  0 1 0 1 2 0 2 3 0 3 0 0 4 5 0 5 6 1 6 7 0
		 7 4 0 8 9 0 9 10 0 10 11 0 11 8 1 12 13 0 13 14 0 14 15 0 15 12 1 16 8 0 11 17 0
		 17 16 0 18 19 0 19 20 0 20 21 0 21 18 1 22 18 0 21 23 0 23 22 0 12 5 0 5 24 0 24 12 0
		 25 7 1 7 16 1 16 25 1 14 3 1 3 9 1 9 14 1 26 17 1 17 20 1 20 26 1 2 23 1 23 10 1
		 10 2 1 15 8 1 8 6 1 6 15 1 26 25 0 11 21 1 25 27 0 27 4 0 1 22 0 19 28 0 28 26 0
		 13 0 0 28 27 0;
	setAttr -s 54 ".n[0:53]" -type "float3"  1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20;
	setAttr -s 25 -ch 94 ".fc[0:24]" -type "polyFaces" 
		f 4 0 1 2 3
		mu 0 4 0 39 1 40
		f 4 4 5 6 7
		mu 0 4 2 3 4 5
		f 4 8 9 10 11
		mu 0 4 6 7 41 8
		f 4 12 13 14 15
		mu 0 4 9 10 11 12
		f 4 16 -12 17 18
		mu 0 4 13 6 8 42
		f 4 19 20 21 22
		mu 0 4 14 43 15 16
		f 4 23 -23 24 25
		mu 0 4 44 14 16 45
		f 3 26 27 28
		mu 0 3 17 18 19
		f 3 29 30 31
		mu 0 3 20 21 22
		f 3 32 33 34
		mu 0 3 23 24 25
		f 3 35 36 37
		mu 0 3 46 47 26
		f 3 38 39 40
		mu 0 3 48 49 50
		f 3 41 42 43
		mu 0 3 27 28 29
		f 4 44 -32 -19 -36
		mu 0 4 46 20 22 47
		f 4 -15 -35 -9 -42
		mu 0 4 27 23 25 28
		f 4 -3 -41 -10 -34
		mu 0 4 24 48 50 25
		f 4 -22 -37 -18 45
		mu 0 4 30 26 47 31
		f 4 -7 -43 -17 -31
		mu 0 4 21 29 28 22
		f 4 -25 -46 -11 -40
		mu 0 4 49 30 31 50
		f 4 -16 -44 -6 -27
		mu 0 4 17 27 29 32
		f 4 46 47 -8 -30
		mu 0 4 20 33 34 21
		f 4 -2 48 -26 -39
		mu 0 4 48 35 36 49
		f 4 -21 49 50 -38
		mu 0 4 26 51 52 46
		f 4 -4 -33 -14 51
		mu 0 4 53 24 23 54
		f 4 52 -47 -45 -51
		mu 0 4 37 55 38 56;
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
connectAttr "Roadstones_1_4Shape.iog" "aiStandardSurface1SG.dsm" -na;
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
// End of Roadstones_1_4.ma
