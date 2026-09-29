//Maya ASCII 2023 scene
//Name: Rock_2_6.ma
//Last modified: Mon, Aug 01, 2022 04:22:59 PM
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
fileInfo "UUID" "BA5B8700-4CE4-0AE1-BAD7-F4B31F0AA4B1";
createNode transform -n "Rock_2_6";
	rename -uid "D81CB0E9-42BB-309D-4C3E-F1A7AF1AD40A";
	setAttr ".t" -type "double3" -679.281005859375 0.50750017166137695 -361.3204345703125 ;
	setAttr ".rp" -type "double3" 679.281005859375 -0.50750017166137695 361.3204345703125 ;
	setAttr ".sp" -type "double3" 679.281005859375 -0.50750017166137695 361.3204345703125 ;
createNode mesh -n "Rock_2_6Shape" -p "Rock_2_6";
	rename -uid "0EDDD2C3-4978-30DB-67D6-5DB6AFD5C368";
	setAttr -k off ".v";
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".uvst[0].uvsn" -type "string" "map1";
	setAttr -s 96 ".uvst[0].uvsp[0:95]" -type "float2" 0.5614 0.74870002
		 0.5614 0.8247 0.56 0.8247 0.56 0.74870002 0.56300002 0.8247 0.5625 0.85970002 0.56150001
		 0.85970002 0.56150001 0.8247 0.55970001 0.74870002 0.5596 0.74870002 0.56129998 0.74870002
		 0.55989999 0.74870002 0.55989999 0.82389998 0.5596 0.80930001 0.5596 0.80949998 0.56129998
		 0.82410002 0.56290001 0.8247 0.56290001 0.74870002 0.55989999 0.8247 0.56029999 0.85960001
		 0.56129998 0.85970002 0.5614 0.82309997 0.5625 0.82309997 0.56239998 0.82309997 0.5614
		 0.85970002 0.56239998 0.85970002 0.56129998 0.82419997 0.5625 0.8603 0.56040001 0.85970002
		 0.56040001 0.86019999 0.56029999 0.8599 0.56300002 0.74870002 0.56150001 0.74870002
		 0.55989999 0.82410002 0.55989999 0.80930001 0.56 0.80930001 0.56029999 0.87559998
		 0.56029999 0.87730002 0.56029999 0.87540001 0.56040001 0.87580001 0.56040001 0.87550002
		 0.56050003 0.87730002 0.5614 0.87550002 0.56150001 0.87550002 0.5614 0.87730002 0.5625
		 0.87580001 0.5625 0.87730002 0.5625 0.87550002 0.56239998 0.87540001 0.56239998 0.87730002
		 0.56129998 0.87540001 0.5614 0.87540001 0.56129998 0.80930001 0.5614 0.80930001 0.55970001
		 0.80930001 0.56150001 0.80930001 0.56150001 0.85460001 0.5614 0.85460001 0.56300002
		 0.85460001 0.56300002 0.80930001 0.56129998 0.85420001 0.56 0.85460001 0.55989999
		 0.85409999 0.56290001 0.80930001 0.56290001 0.85460001 0.55989999 0.85460001 0.5596
		 0.84549999 0.56050003 0.82309997 0.56029999 0.82309997 0.5596 0.74870002 0.5614 0.74870002
		 0.5614 0.8247 0.5614 0.82309997 0.56300002 0.8247 0.5625 0.8603 0.56300002 0.8247
		 0.5614 0.85970002 0.55989999 0.8247 0.56300002 0.74870002 0.56300002 0.74870002 0.55989999
		 0.80930001 0.5625 0.87580001 0.5614 0.87730002 0.55970001 0.80930001 0.5614 0.80930001
		 0.56300002 0.85460001 0.56300002 0.80930001 0.5614 0.85460001 0.56300002 0.80930001
		 0.56300002 0.85460001 0.55989999 0.85460001 0.5596 0.84549999 0.5596 0.80930001 0.5596
		 0.80930001 0.55970001 0.74870002 0.55989999 0.74870002;
	setAttr ".cuvs" -type "string" "map1";
	setAttr ".dcc" -type "string" "Ambient+Diffuse";
	setAttr -s 47 ".vt[0:46]"  674.38916016 -0.50750017 361.89672852 674.38916016 4.59717941 361.89672852
		 675.61328125 4.59717941 354.55493164 675.61376953 -0.50750017 354.55395508 677.23876953 4.59719086 370.059814453
		 677.88330078 6.94963837 367.53149414 675.97900391 6.94984055 362.30249023 674.43310547 4.59717941 362.36889648
		 682.70166016 -0.50750017 353.13891602 683.00390625 -0.50750017 352.61010742 684.171875 -0.50750017 361.3972168
		 675.89257813 -0.50750017 354.22680664 675.89013672 4.54597092 354.22753906 682.76953125 3.56702042 352.34790039
		 682.77978516 -0.50750017 352.3449707 683.00390625 3.5748291 352.6105957 684.17285156 4.55741119 361.40625
		 684.15234375 -0.50750017 361.96484375 684.15380859 4.59717941 361.95703125 682.87939453 4.59719086 369.67822266
		 682.87939453 -0.50750017 369.67919922 682.46435547 4.59717941 354.24194336 681.61474609 6.93962097 356.12768555
		 682.73632813 6.94715881 361.48852539 676.28222656 7.15653229 362.042480469 678.19921875 7.15653229 367.30786133
		 681.52539063 7.15653229 367.085693359 682.41162109 7.15653229 361.74047852 682.73535156 6.94639969 362.035400391
		 681.86914063 6.9466095 367.26342773 682.58837891 4.59719086 369.96142578 681.55957031 6.98855972 367.50537109
		 678.23339844 6.98855972 367.72729492 677.57763672 4.59719086 370.29589844 675.93603516 6.95137024 361.83007813
		 676.76269531 6.95116043 356.85327148 677.071289063 6.98759842 356.58276367 681.36083984 6.95985031 355.9074707
		 682.21630859 4.59717941 353.98657227 677.23925781 -0.50750017 370.060791016 674.43310547 -0.50750017 362.36889648
		 682.58837891 -0.50750017 369.96142578 677.57763672 -0.50750017 370.29589844 675.89794922 -0.50750017 354.25146484
		 681.29003906 7.15653229 356.31274414 677.11914063 7.15653229 357.00048828125 682.31933594 -0.50750017 353.19238281;
	setAttr -s 92 ".ed[0:91]"  0 1 1 1 2 0 2 3 0 3 0 0 4 5 0 5 6 1 6 7 1
		 7 4 0 8 9 1 9 10 0 10 8 1 11 12 0 12 13 0 13 14 0 14 11 0 9 15 0 15 16 0 16 10 1
		 17 18 1 18 19 0 19 20 0 20 17 0 21 22 1 22 23 0 23 16 1 16 21 1 24 25 1 25 26 1 26 27 1
		 27 24 1 18 28 1 28 29 1 29 19 0 15 21 1 30 31 1 31 32 1 32 33 1 33 30 0 1 34 1 34 35 1
		 35 2 0 12 36 1 36 37 1 37 38 0 38 12 1 39 4 0 7 40 1 40 39 0 38 13 1 41 30 0 33 42 0
		 42 41 0 11 43 1 43 3 0 3 11 0 37 44 1 44 22 1 22 37 1 36 35 1 35 45 1 45 36 1 34 6 1
		 6 24 1 24 34 1 32 25 1 25 5 1 5 32 1 31 29 1 29 26 1 26 31 1 23 27 1 27 28 1 28 23 1
		 10 17 0 17 46 0 46 8 1 0 40 0 7 1 0 33 4 0 39 42 0 16 18 0 2 12 0 41 20 0 19 30 0
		 45 44 1 24 45 1 44 27 0 21 38 1 13 15 0 9 14 0 46 14 1 46 43 0;
	setAttr -s 84 ".n[0:83]" -type "float3"  1e+20 1e+20 1e+20 1e+20 1e+20
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
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20;
	setAttr -s 46 -ch 174 ".fc[0:45]" -type "polyFaces" 
		f 4 0 1 2 3
		mu 0 4 0 1 2 3
		f 4 4 5 6 7
		mu 0 4 4 5 6 7
		f 3 8 9 10
		mu 0 3 8 9 10
		f 4 11 12 13 14
		mu 0 4 11 12 13 69
		f 4 15 16 17 -10
		mu 0 4 9 14 15 10
		f 4 18 19 20 21
		mu 0 4 70 71 16 17
		f 4 22 23 24 25
		mu 0 4 18 19 20 15
		f 4 26 27 28 29
		mu 0 4 21 22 23 72
		f 4 30 31 32 -20
		mu 0 4 71 24 25 16
		f 3 -17 33 -26
		mu 0 3 26 14 18
		f 4 34 35 36 37
		mu 0 4 73 27 74 75
		f 4 38 39 40 -2
		mu 0 4 1 76 28 2
		f 4 41 42 43 44
		mu 0 4 12 29 30 77
		f 4 45 -8 46 47
		mu 0 4 31 4 7 32
		f 3 48 -13 -45
		mu 0 3 77 13 33
		f 4 49 -38 50 51
		mu 0 4 78 73 75 79
		f 3 52 53 54
		mu 0 3 34 80 35
		f 3 55 56 57
		mu 0 3 36 37 38
		f 3 58 59 60
		mu 0 3 39 40 41
		f 3 61 62 63
		mu 0 3 42 43 44
		f 3 64 65 66
		mu 0 3 45 46 47
		f 3 67 68 69
		mu 0 3 81 48 49
		f 3 70 71 72
		mu 0 3 50 82 51
		f 4 73 74 75 -11
		mu 0 4 52 53 54 83
		f 4 76 -47 77 -1
		mu 0 4 84 55 56 57
		f 4 78 -46 79 -51
		mu 0 4 58 85 59 86
		f 4 -74 -18 80 -19
		mu 0 4 53 52 60 87
		f 4 -55 -3 81 -12
		mu 0 4 34 35 61 62
		f 4 82 -21 83 -50
		mu 0 4 88 63 64 89
		f 4 -56 -43 -61 84
		mu 0 4 37 36 39 41
		f 4 -60 -40 -64 85
		mu 0 4 41 40 42 44
		f 4 -65 -36 -70 -28
		mu 0 4 46 45 81 49
		f 4 -71 -24 -57 86
		mu 0 4 82 50 38 37
		f 4 -69 -32 -72 -29
		mu 0 4 49 48 51 82
		f 4 -63 -6 -66 -27
		mu 0 4 44 43 47 46
		f 4 -82 -41 -59 -42
		mu 0 4 62 61 40 39
		f 4 -62 -39 -78 -7
		mu 0 4 43 42 57 56
		f 4 -84 -33 -68 -35
		mu 0 4 89 64 48 81
		f 4 -73 -31 -81 -25
		mu 0 4 50 51 87 60
		f 4 -79 -37 -67 -5
		mu 0 4 85 58 45 47
		f 4 87 -44 -58 -23
		mu 0 4 65 90 36 38
		f 4 88 -16 89 -14
		mu 0 4 66 91 92 93
		f 4 -89 -49 -88 -34
		mu 0 4 91 66 90 65
		f 4 -76 90 -90 -9
		mu 0 4 83 54 93 92
		f 4 -15 -91 91 -53
		mu 0 4 11 69 94 95
		f 4 -86 -30 -87 -85
		mu 0 4 67 21 72 68;
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
connectAttr "Rock_2_6Shape.iog" "aiStandardSurface1SG.dsm" -na;
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
// End of Rock_2_6.ma
