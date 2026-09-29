//Maya ASCII 2023 scene
//Name: Roadstones_1_6.ma
//Last modified: Mon, Aug 01, 2022 04:24:16 PM
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
fileInfo "UUID" "203B222C-4691-E255-FD7D-87BA05526A0D";
createNode transform -n "Roadstones_1_6";
	rename -uid "CA40059F-420C-5223-E4D1-AD95835DAC61";
	setAttr ".t" -type "double3" -600.147705078125 0.14993000030517578 -250.554931640625 ;
	setAttr ".rp" -type "double3" 600.147705078125 -0.14993000030517578 250.554931640625 ;
	setAttr ".sp" -type "double3" 600.147705078125 -0.14993000030517578 250.554931640625 ;
createNode mesh -n "Roadstones_1_6Shape" -p "Roadstones_1_6";
	rename -uid "C1367FEF-485A-662C-181E-C89C004ABE31";
	setAttr -k off ".v";
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".uvst[0].uvsn" -type "string" "map1";
	setAttr -s 61 ".uvst[0].uvsp[0:60]" -type "float2" 0.68120003 0.72659999
		 0.6807 0.72659999 0.6803 0.82669997 0.6807 0.82669997 0.6778 0.72659999 0.67549998
		 0.72659999 0.67589998 0.82550001 0.6778 0.82550001 0.67830002 0.72659999 0.68049997
		 0.72659999 0.68010002 0.82550001 0.67820001 0.82550001 0.67479998 0.72659999 0.67580003
		 0.72659999 0.67610002 0.82669997 0.6753 0.82669997 0.67629999 0.81470001 0.67820001
		 0.81470001 0.67559999 0.81470001 0.68049997 0.81470001 0.68010002 0.81470001 0.67790002
		 0.81470001 0.676 0.81470001 0.676 0.72659999 0.67629999 0.82550001 0.6753 0.72659999
		 0.67570001 0.82669997 0.67629999 0.8836 0.67629999 0.90109998 0.67610002 0.88480002
		 0.6803 0.88480002 0.68010002 0.90109998 0.68010002 0.8836 0.67570001 0.88480002 0.676
		 0.90109998 0.67589998 0.88370001 0.68010002 0.88370001 0.67559999 0.90109998 0.6753
		 0.88480002 0.67820001 0.90109998 0.67820001 0.8836 0.68049997 0.90109998 0.6807 0.88480002
		 0.67790002 0.90109998 0.6778 0.88370001 0.67549998 0.78479999 0.6753 0.78479999 0.67580003
		 0.78479999 0.676 0.78479999 0.68049997 0.78479999 0.6807 0.78479999 0.67820001 0.81470001
		 0.68010002 0.81470001 0.68049997 0.72659999 0.68010002 0.82550001 0.6807 0.72659999
		 0.6803 0.82669997 0.68010002 0.90109998 0.6803 0.88480002 0.68049997 0.78479999 0.6807
		 0.78479999;
	setAttr ".cuvs" -type "string" "map1";
	setAttr ".dcc" -type "string" "Ambient+Diffuse";
	setAttr -s 33 ".vt[0:32]"  606.71337891 -0.14991999 250.57788086 605.73583984 -0.14993 247.13037109
		 604.90869141 1.39990997 247.70678711 605.72216797 1.39990997 250.57568359 599.64990234 -0.14993 246.0048828125
		 594.96240234 -0.14993 246.74462891 595.83056641 1.38226032 247.32128906 599.75146484 1.38222027 246.70263672
		 600.64501953 -0.14991999 255.10498047 605.3359375 -0.14991999 254.36474609 604.51855469 1.38195992 253.79052734
		 600.59423828 1.38193989 254.40966797 593.58203125 -0.14991999 250.53198242 595.49414063 -0.14991999 254.053710938
		 596.21875 1.40028 253.47241211 594.62451172 1.4004097 250.53662109 596.65039063 1.65182018 253.36694336
		 600.58544922 1.65182018 253.98779297 600.58544922 1.65182018 250.57519531 595.11474609 1.65182018 250.53955078
		 605.25341797 1.65182018 250.57519531 604.45751953 1.65182018 247.76806641 599.83447266 1.65182018 247.12353516
		 595.90673828 1.65182018 247.74291992 604.45947266 1.65182018 253.37646484 595.94726563 -0.14991999 254.36376953
		 596.66308594 1.38191986 253.78955078 605.33398438 -0.14993 246.79663086 604.51660156 1.38218975 247.36645508
		 594.55957031 -0.14993 247.083984375 595.43798828 1.40052986 247.66772461 605.73583984 -0.14991999 254.025390625
		 604.90869141 1.39990997 253.44433594;
	setAttr -s 60 ".ed[0:59]"  0 1 0 1 2 1 2 3 1 3 0 1 4 5 0 5 6 1 6 7 0
		 7 4 1 8 9 0 9 10 1 10 11 0 11 8 1 12 13 0 13 14 1 14 15 1 15 12 0 16 17 0 17 18 1
		 18 19 1 19 16 0 18 20 1 20 21 1 21 22 0 22 18 1 22 23 0 23 19 1 17 24 0 24 20 1 25 8 0
		 11 26 0 26 25 1 27 4 0 7 28 0 28 27 1 29 12 0 15 30 1 30 29 1 31 0 0 3 32 1 32 31 1
		 26 16 1 16 14 1 14 26 1 32 24 1 24 10 1 10 32 1 30 23 1 23 6 1 6 30 1 28 21 1 21 2 1
		 2 28 1 15 19 1 11 17 1 3 20 1 7 22 1 5 29 0 13 25 0 9 31 0 1 27 0;
	setAttr -s 39 ".n[0:38]" -type "float3"  1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20;
	setAttr -s 28 -ch 108 ".fc[0:27]" -type "polyFaces" 
		f 4 0 1 2 3
		mu 0 4 0 1 2 3
		f 4 4 5 6 7
		mu 0 4 4 5 6 7
		f 4 8 9 10 11
		mu 0 4 8 9 10 11
		f 4 12 13 14 15
		mu 0 4 12 13 14 15
		f 4 16 17 18 19
		mu 0 4 16 17 51 18
		f 4 20 21 22 23
		mu 0 4 51 19 20 21
		f 4 -19 -24 24 25
		mu 0 4 18 51 21 22
		f 4 26 27 -21 -18
		mu 0 4 17 52 19 51
		f 4 28 -12 29 30
		mu 0 4 23 8 11 24
		f 4 31 -8 32 33
		mu 0 4 53 4 7 54
		f 4 34 -16 35 36
		mu 0 4 25 12 15 26
		f 4 37 -4 38 39
		mu 0 4 55 0 3 56
		f 3 40 41 42
		mu 0 3 27 28 29
		f 3 43 44 45
		mu 0 3 30 31 32
		f 3 46 47 48
		mu 0 3 33 34 35
		f 3 49 50 51
		mu 0 3 36 57 58
		f 4 -26 -47 -36 52
		mu 0 4 37 34 33 38
		f 4 -17 -41 -30 53
		mu 0 4 39 28 27 40
		f 4 -28 -44 -39 54
		mu 0 4 41 31 30 42
		f 4 -23 -50 -33 55
		mu 0 4 43 57 36 44
		f 4 -22 -55 -3 -51
		mu 0 4 57 41 42 58
		f 4 -25 -56 -7 -48
		mu 0 4 34 43 44 35
		f 4 -27 -54 -11 -45
		mu 0 4 31 39 40 32
		f 4 -20 -53 -15 -42
		mu 0 4 28 37 38 29
		f 4 -6 56 -37 -49
		mu 0 4 35 45 46 33
		f 4 -14 57 -31 -43
		mu 0 4 29 47 48 27
		f 4 -10 58 -40 -46
		mu 0 4 32 49 50 30
		f 4 -34 -52 -2 59
		mu 0 4 59 36 58 60;
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
connectAttr "Roadstones_1_6Shape.iog" "aiStandardSurface1SG.dsm" -na;
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
// End of Roadstones_1_6.ma
