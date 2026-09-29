//Maya ASCII 2023 scene
//Name: Rock_1_1.ma
//Last modified: Mon, Aug 01, 2022 04:21:04 PM
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
fileInfo "UUID" "FC0C2EB2-4D3E-22D1-B47D-87B8CBBD96DC";
createNode transform -n "Rock_1_1";
	rename -uid "27C4AC24-436A-AFD7-0EEF-23AB9CB0BF18";
	setAttr ".t" -type "double3" -558.6318359375 0.97198963165283203 -402.5604248046875 ;
	setAttr ".rp" -type "double3" 558.6318359375 -0.97198963165283203 402.5604248046875 ;
	setAttr ".sp" -type "double3" 558.6318359375 -0.97198963165283203 402.5604248046875 ;
createNode mesh -n "Rock_1_1Shape" -p "Rock_1_1";
	rename -uid "EC60200D-418F-5BBB-BF25-CAA1488AA2A1";
	setAttr -k off ".v";
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".uvst[0].uvsn" -type "string" "map1";
	setAttr -s 85 ".uvst[0].uvsp[0:84]" -type "float2" 0.6832 0.8211 0.68379998
		 0.85589999 0.68400002 0.84979999 0.68339998 0.81819999 0.68379998 0.81819999 0.68419999
		 0.84640002 0.68559998 0.85570002 0.68559998 0.83600003 0.6875 0.81770003 0.68720001
		 0.84189999 0.68730003 0.8448 0.68760002 0.81919998 0.68559998 0.81239998 0.68559998
		 0.82560003 0.68730003 0.80489999 0.68709999 0.79820001 0.68559998 0.80870003 0.68699998
		 0.79519999 0.6857 0.76800001 0.68559998 0.85210001 0.68339998 0.82429999 0.68290001
		 0.7712 0.68699998 0.8423 0.68730003 0.8193 0.68409997 0.84680003 0.68360001 0.81669998
		 0.68559998 0.87470001 0.6839 0.8581 0.68760002 0.82590002 0.68730003 0.85360003 0.68419999
		 0.80260003 0.68400002 0.8096 0.68430001 0.79949999 0.68830001 0.77389997 0.68849999
		 0.77280003 0.6857 0.77509999 0.68809998 0.77420002 0.68269998 0.77170002 0.68300003
		 0.7737 0.68779999 0.82239997 0.68879998 0.77060002 0.6875 0.8506 0.68809998 0.89209998
		 0.68839997 0.89209998 0.68800002 0.89209998 0.68279999 0.89209998 0.68239999 0.89209998
		 0.68260002 0.89209998 0.68769997 0.89209998 0.68790001 0.89200002 0.68760002 0.89200002
		 0.6832 0.89209998 0.68290001 0.89209998 0.68889999 0.89200002 0.6886 0.89200002 0.68529999
		 0.89209998 0.68150002 0.89200002 0.6807 0.8919 0.68089998 0.89179999 0.68169999 0.89200002
		 0.68309999 0.89209998 0.68269998 0.89209998 0.6821 0.89200002 0.68239999 0.89200002
		 0.68839997 0.89200002 0.68970001 0.8919 0.6893 0.8919 0.68800002 0.89200002 0.68779999
		 0.89209998 0.69050002 0.89179999 0.69029999 0.89179999 0.68870002 0.7701 0.6832 0.77469999
		 0.68339998 0.77499998 0.68180001 0.8919 0.6814 0.8919 0.6832 0.89209998 0.68529999
		 0.89209998 0.68239999 0.89200002 0.6821 0.89200002 0.68529999 0.89209998 0.68529999
		 0.89209998 0.68809998 0.89209998 0.68360001 0.81669998 0.68379998 0.81819999;
	setAttr ".cuvs" -type "string" "map1";
	setAttr ".dcc" -type "string" "Ambient+Diffuse";
	setAttr -s 47 ".vt[0:46]"  551.069335938 8.66588593 396.46655273 552.024902344 16.13960266 398.10351563
		 555.47949219 16.52470398 396.84545898 555.49316406 9.24809265 395.20825195 559.31835938 9.12960815 394.86743164
		 560.086425781 16.25541687 396.48168945 563.93261719 16.17407227 401.088134766 564.30224609 11.42127228 400.68554688
		 565.68115234 8.66590118 407.67456055 565.3203125 14.49940491 407.056396484 561.85253906 14.88449097 407.76708984
		 563.18212891 9.99214935 408.38525391 558.65478516 17.14332581 402.55517578 553.1796875 16.89930725 404.11938477
		 557.83740234 15.64350891 408.51489258 561.51757813 16.028610229 407.19262695 562.89599609 16.96138 401.3828125
		 564.98535156 15.64350891 406.48193359 550.023925781 -0.97198009 405.016845703 551.27685547 13.79035187 404.66040039
		 550.37548828 9.14019775 397.42773438 549.78027344 -0.97198963 396.3059082 565.77197266 14.83630371 406.2253418
		 566.29345703 9.17761993 406.7902832 558.94726563 16.13960266 396.13476563 558.51074219 9.3355484 394.49780273
		 552.33251953 16.28062439 404.36010742 551.20947266 16.21127319 398.97583008 557.29980469 9.18196869 409.34204102
		 556.92773438 14.78529358 408.76538086 555.88525391 17.51930237 397.54052734 552.17675781 17.13420105 398.87060547
		 559.35302734 17.13420105 396.82983398 566.87451172 -0.97198009 409.71948242 564.37548828 -0.97198009 410.43017578
		 565.34814453 -0.79560995 400.68554688 567.48339844 -0.97198009 408.95263672 550.44775391 -0.97198963 395.40136719
		 554.87158203 -0.97198963 394.14331055 558.75830078 8.66590118 409.64331055 559.95166016 -0.97198009 411.68823242
		 558.39794922 14.49940491 409.025146484 559.63720703 8.81269836 394.32958984 558.82958984 9.018638611 393.95996094
		 558.64599609 -0.97198009 411.44042969 557.37060547 -0.97198963 393.43261719 558.63964844 -0.97198963 393.76245117;
	setAttr -s 89 ".ed[0:88]"  0 1 1 1 2 1 2 3 1 3 0 1 4 5 1 5 6 0 6 7 1
		 7 4 0 8 9 0 9 10 1 10 11 1 11 8 1 12 13 1 13 14 0 14 15 0 15 12 1 16 12 1 15 17 0
		 17 16 0 18 19 0 19 20 1 20 21 0 21 18 0 6 22 0 22 23 0 23 7 1 2 24 1 24 25 0 25 3 0
		 19 26 0 26 27 0 27 20 0 28 29 1 29 26 0 19 28 1 30 31 0 31 13 0 12 30 1 32 30 0 16 32 0
		 33 8 0 11 34 1 34 33 0 35 7 1 23 36 0 36 35 0 37 0 0 3 38 1 38 37 0 11 39 1 39 40 1
		 40 34 0 10 41 1 41 39 1 29 41 1 41 14 1 14 29 0 31 1 1 1 27 1 27 31 0 17 9 0 9 22 1
		 22 17 0 32 5 0 5 24 1 24 32 1 28 39 1 26 13 0 37 21 0 20 0 1 2 30 1 25 4 0 4 42 1
		 42 43 0 43 25 0 6 16 1 33 36 0 23 8 1 10 15 1 28 44 1 44 40 0 18 44 0 3 43 0 43 45 0
		 45 38 0 46 42 0 42 7 0 35 46 0 46 45 0;
	setAttr -s 94 ".n[0:93]" -type "float3"  1e+20 1e+20 1e+20 1e+20 1e+20
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
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20;
	setAttr -s 43 -ch 166 ".fc[0:42]" -type "polyFaces" 
		f 4 0 1 2 3
		mu 0 4 0 1 2 3
		f 4 4 5 6 7
		mu 0 4 4 5 6 7
		f 4 8 9 10 11
		mu 0 4 8 9 10 11
		f 4 12 13 14 15
		mu 0 4 12 13 14 15
		f 4 16 -16 17 18
		mu 0 4 16 12 15 17
		f 4 19 20 21 22
		mu 0 4 18 19 20 21
		f 4 -7 23 24 25
		mu 0 4 7 6 22 23
		f 4 -3 26 27 28
		mu 0 4 3 2 24 25
		f 4 29 30 31 -21
		mu 0 4 19 26 27 20
		f 4 32 33 -30 34
		mu 0 4 28 29 26 19
		f 4 35 36 -13 37
		mu 0 4 30 31 13 12
		f 4 38 -38 -17 39
		mu 0 4 32 30 12 16
		f 4 40 -12 41 42
		mu 0 4 33 8 11 34
		f 4 43 -26 44 45
		mu 0 4 35 7 23 36
		f 4 46 -4 47 48
		mu 0 4 37 0 3 38
		f 4 -42 49 50 51
		mu 0 4 34 11 39 40
		f 4 -11 52 53 -50
		mu 0 4 11 10 41 39
		f 3 54 55 56
		mu 0 3 42 43 44
		f 3 57 58 59
		mu 0 3 45 46 47
		f 3 60 61 62
		mu 0 3 48 49 50
		f 3 63 64 65
		mu 0 3 51 76 52
		f 4 -54 -55 -33 66
		mu 0 4 53 43 42 54
		f 4 -37 -60 -31 67
		mu 0 4 55 45 47 77
		f 4 -47 68 -22 69
		mu 0 4 56 57 58 59
		f 4 -39 -66 -27 70
		mu 0 4 60 51 52 61
		f 4 71 72 73 74
		mu 0 4 62 63 78 79
		f 4 -19 -63 -24 75
		mu 0 4 80 48 50 81
		f 4 -41 76 -45 77
		mu 0 4 64 65 66 67
		f 4 -15 -56 -53 78
		mu 0 4 68 44 43 82
		f 4 -51 -67 79 80
		mu 0 4 69 53 54 70
		f 4 -14 -68 -34 -57
		mu 0 4 44 55 77 42
		f 4 -1 -70 -32 -59
		mu 0 4 46 56 59 47
		f 4 -36 -71 -2 -58
		mu 0 4 45 60 61 46
		f 4 -5 -72 -28 -65
		mu 0 4 76 63 62 52
		f 4 -40 -76 -6 -64
		mu 0 4 51 80 81 76
		f 4 -9 -78 -25 -62
		mu 0 4 49 64 67 50
		f 4 -18 -79 -10 -61
		mu 0 4 48 68 82 49
		f 4 -80 -35 -20 81
		mu 0 4 71 28 19 18
		f 4 -48 82 83 84
		mu 0 4 38 3 83 72
		f 4 85 86 -44 87
		mu 0 4 73 84 7 35
		f 4 -86 88 -84 -74
		mu 0 4 78 74 75 79
		f 3 -8 -87 -73
		mu 0 3 4 7 84
		f 3 -29 -75 -83
		mu 0 3 3 25 83;
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
connectAttr "Rock_1_1Shape.iog" "aiStandardSurface1SG.dsm" -na;
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
// End of Rock_1_1.ma
