//Maya ASCII 2023 scene
//Name: Rock_1_4.ma
//Last modified: Mon, Aug 01, 2022 04:22:15 PM
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
fileInfo "UUID" "2FAC6C36-4669-00C5-F2B1-8FABF12E4F3D";
createNode transform -n "Rock_1_4";
	rename -uid "6638F8E4-448B-FA6E-20A6-9592B9DF23C5";
	setAttr ".t" -type "double3" -634.9736328125 0.64853000640869141 -398.823974609375 ;
	setAttr ".rp" -type "double3" 634.9736328125 -0.64853000640869141 398.823974609375 ;
	setAttr ".sp" -type "double3" 634.9736328125 -0.64853000640869141 398.823974609375 ;
createNode mesh -n "Rock_1_4Shape" -p "Rock_1_4";
	rename -uid "B50EE6C9-482F-5D68-4A4B-9DA3D786F4DA";
	setAttr -k off ".v";
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".uvst[0].uvsn" -type "string" "map1";
	setAttr -s 88 ".uvst[0].uvsp[0:87]" -type "float2" 0.67769998 0.73360002
		 0.67729998 0.73360002 0.67750001 0.79290003 0.6778 0.79470003 0.68239999 0.84909999
		 0.68019998 0.82270002 0.67760003 0.7859 0.68080002 0.83050001 0.68099999 0.81059998
		 0.67790002 0.79549998 0.67790002 0.83859998 0.6803 0.87190002 0.68169999 0.81950003
		 0.68379998 0.8301 0.68260002 0.8998 0.68099999 0.88129997 0.67790002 0.78909999 0.68379998
		 0.82999998 0.68110001 0.81550002 0.68049997 0.87419999 0.68260002 0.89969999 0.68419999
		 0.82489997 0.68159997 0.81040001 0.68260002 0.73360002 0.68519998 0.73360002 0.68419999
		 0.82499999 0.6821 0.81440002 0.6821 0.73360002 0.67739999 0.73360002 0.68220001 0.7626
		 0.68150002 0.81519997 0.67760003 0.79369998 0.68169999 0.76029998 0.68099999 0.81160003
		 0.6814 0.80699998 0.68150002 0.81580001 0.68190002 0.81099999 0.67760003 0.83380002
		 0.6778 0.83700001 0.68150002 0.81529999 0.68080002 0.87889999 0.67769998 0.83539999
		 0.67940003 0.85909998 0.67949998 0.8574 0.67940003 0.85680002 0.67930001 0.85540003
		 0.67940003 0.85610002 0.67930001 0.85769999 0.6807 0.8743 0.6807 0.87529999 0.6807
		 0.87629998 0.6814 0.88410002 0.6814 0.88300002 0.6814 0.8829 0.68049997 0.87230003
		 0.68040001 0.87129998 0.68040001 0.87309998 0.67930001 0.8387 0.67930001 0.83840001
		 0.67940003 0.83939999 0.67940003 0.8136 0.67940003 0.8391 0.68190002 0.8538 0.68190002
		 0.85390002 0.67930001 0.8136 0.67919999 0.8136 0.68099999 0.84789997 0.68110001 0.8459
		 0.68120003 0.84729999 0.68099999 0.8495 0.6821 0.85170001 0.68099999 0.8477 0.68080002
		 0.84780002 0.68080002 0.84579998 0.68099999 0.84560001 0.68089998 0.84429997 0.68080002
		 0.84619999 0.6825 0.8136 0.68120003 0.8136 0.68099999 0.8247 0.68129998 0.82569999
		 0.6814 0.8136 0.68190002 0.73360002 0.6778 0.73360002 0.68519998 0.73360002 0.67940003
		 0.8136 0.6821 0.85170001 0.6825 0.8136;
	setAttr ".cuvs" -type "string" "map1";
	setAttr ".dcc" -type "string" "Ambient+Diffuse";
	setAttr -s 41 ".vt[0:40]"  626.99658203 -0.64853001 394.89916992 626.12744141 -0.64853001 405.35742188
		 626.44091797 3.40345955 404.036376953 627.098144531 3.52634048 395.87670898 637.64746094 10.89202118 399.56347656
		 632.69921875 9.083763123 392.73291016 626.83691406 6.5696907 403.027587891 633.97070313 9.6121521 405.46948242
		 634.40966797 4.61553955 390.68969727 627.37109375 3.57743073 395.40527344 627.43261719 6.52761078 396.08203125
		 632.75195313 8.79619598 392.45849609 635.89257813 5.22220993 407.032470703 640.78125 5.94260025 399.80615234
		 638.018066406 10.70864868 399.76025391 634.32226563 9.44313049 405.69458008 627.35302734 6.79117966 396.41821289
		 640.77197266 5.93814087 399.2878418 634.70361328 4.94419861 390.93701172 633.18066406 8.95941925 392.55322266
		 638.0014648438 10.69885254 399.25219727 641.66845703 5.58808899 399.28759766 635.69189453 4.59424973 390.93774414
		 638.061035156 -0.64853001 408.88769531 643.81982422 -0.64853001 399.8737793 641.67773438 5.59254837 399.80615234
		 636.86132813 4.87223053 407.031982422 643.81542969 -0.64853001 399.33764648 636.81787109 -0.64853001 388.68261719
		 626.39013672 -0.64853001 405.7590332 637.60400391 -0.64853001 409.066162109 635.52734375 4.9328804 407.30224609
		 626.70068359 3.45388985 404.44458008 636.39111328 -0.64853001 388.58178711 635.24853516 4.36811066 390.54321289
		 636.42822266 4.64046097 407.40454102 626.65673828 6.19826889 403.12524414 627.16894531 6.41637039 396.5534668
		 633.88671875 9.27890778 405.87182617 626.91162109 6.30947876 403.54003906 627.27685547 -0.64853001 394.42749023;
	setAttr -s 79 ".ed[0:78]"  0 1 0 1 2 0 2 3 1 3 0 1 4 5 0 5 6 1 6 7 0
		 7 4 0 8 9 1 9 10 1 10 11 1 11 8 0 12 13 0 13 14 0 14 15 0 15 12 0 5 16 0 16 6 0 17 18 0
		 18 19 0 19 20 0 20 17 0 17 21 1 21 22 0 22 18 1 23 24 0 24 25 0 25 26 0 26 23 1 27 28 0
		 28 22 1 21 27 0 29 30 0 30 31 1 31 32 1 32 29 0 33 8 0 8 34 1 34 33 1 30 35 1 35 31 1
		 2 36 0 36 37 1 37 3 1 12 26 0 25 13 1 31 38 0 38 39 0 39 32 0 16 10 1 10 37 1 37 16 1
		 36 39 1 39 6 1 6 36 1 38 15 0 15 7 1 7 38 1 4 14 1 14 20 0 20 4 1 19 11 1 11 5 0
		 5 19 1 2 32 1 9 40 1 40 0 0 3 9 1 13 17 0 1 29 0 35 26 1 12 31 1 25 21 0 18 8 1 22 34 1
		 24 27 0 28 33 0 30 23 0 33 40 0;
	setAttr -s 78 ".n[0:77]" -type "float3"  1e+20 1e+20 1e+20 1e+20 1e+20
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
		 1e+20 1e+20 1e+20 1e+20 1e+20;
	setAttr -s 39 -ch 148 ".fc[0:38]" -type "polyFaces" 
		f 4 0 1 2 3
		mu 0 4 0 1 2 3
		f 4 4 5 6 7
		mu 0 4 4 5 6 7
		f 4 8 9 10 11
		mu 0 4 8 9 10 11
		f 4 12 13 14 15
		mu 0 4 12 13 14 15
		f 3 16 17 -6
		mu 0 3 5 16 6
		f 4 18 19 20 21
		mu 0 4 17 18 19 20
		f 4 -19 22 23 24
		mu 0 4 18 17 21 22
		f 4 25 26 27 28
		mu 0 4 23 24 25 26
		f 4 29 30 -24 31
		mu 0 4 84 27 22 21
		f 4 32 33 34 35
		mu 0 4 28 29 30 31
		f 3 36 37 38
		mu 0 3 32 33 34
		f 3 -34 39 40
		mu 0 3 35 29 36
		f 4 -3 41 42 43
		mu 0 4 3 2 37 38
		f 4 -13 44 -28 45
		mu 0 4 13 12 26 25
		f 4 -35 46 47 48
		mu 0 4 31 39 40 41
		f 3 49 50 51
		mu 0 3 42 43 44
		f 3 52 53 54
		mu 0 3 45 46 47
		f 3 55 56 57
		mu 0 3 48 49 50
		f 3 58 59 60
		mu 0 3 51 52 53
		f 3 61 62 63
		mu 0 3 54 55 56
		f 4 -43 -55 -18 -52
		mu 0 4 44 45 47 42
		f 4 -48 -58 -7 -54
		mu 0 4 46 48 50 47
		f 4 -49 -53 -42 64
		mu 0 4 57 46 45 58
		f 4 65 66 -4 67
		mu 0 4 59 60 85 61
		f 4 -21 -64 -5 -61
		mu 0 4 53 54 56 51
		f 4 -22 -60 -14 68
		mu 0 4 62 53 52 63
		f 4 -36 -65 -2 69
		mu 0 4 64 57 58 65
		f 4 -10 -68 -44 -51
		mu 0 4 43 59 61 44
		f 4 -41 70 -45 71
		mu 0 4 66 67 68 69
		f 4 -23 -69 -46 72
		mu 0 4 70 62 63 86
		f 4 -11 -50 -17 -63
		mu 0 4 55 43 42 56
		f 4 -15 -59 -8 -57
		mu 0 4 49 52 51 50
		f 4 -47 -72 -16 -56
		mu 0 4 48 71 69 49
		f 4 -20 73 -12 -62
		mu 0 4 54 72 73 55
		f 4 -25 74 -38 -74
		mu 0 4 72 74 75 76
		f 4 -32 -73 -27 75
		mu 0 4 77 70 86 87
		f 4 -31 76 -39 -75
		mu 0 4 74 78 79 75
		f 4 -40 77 -29 -71
		mu 0 4 67 80 81 68
		f 4 78 -66 -9 -37
		mu 0 4 82 83 9 8;
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
connectAttr "Rock_1_4Shape.iog" "aiStandardSurface1SG.dsm" -na;
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
// End of Rock_1_4.ma
