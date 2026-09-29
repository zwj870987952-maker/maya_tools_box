//Maya ASCII 2023 scene
//Name: Rock_1_8.ma
//Last modified: Mon, Aug 01, 2022 04:23:40 PM
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
fileInfo "UUID" "D79A28FB-41E4-3A37-C962-66925D7765C1";
createNode transform -n "Rock_1_8";
	rename -uid "1C3AD669-4713-53F5-18DB-B6ADBA05076F";
	setAttr ".t" -type "double3" -710.36669921875 0.91954994201660156 -399.9036865234375 ;
	setAttr ".rp" -type "double3" 710.36669921875 -0.91954994201660156 399.9036865234375 ;
	setAttr ".sp" -type "double3" 710.36669921875 -0.91954994201660156 399.9036865234375 ;
createNode mesh -n "Rock_1_8Shape" -p "Rock_1_8";
	rename -uid "3F09042F-42E4-13AA-EA14-2891E8284A70";
	setAttr -k off ".v";
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".uvst[0].uvsn" -type "string" "map1";
	setAttr -s 63 ".uvst[0].uvsp[0:62]" -type "float2" 0.68190002 0.79470003
		 0.68080002 0.80260003 0.68049997 0.8362 0.68099999 0.8369 0.67390001 0.80140001 0.67309999
		 0.79479998 0.67400002 0.83749998 0.67449999 0.83639997 0.68409997 0.82419997 0.68279999
		 0.8222 0.67989999 0.82139999 0.68180001 0.82599998 0.67580003 0.78740001 0.6807 0.78759998
		 0.68000001 0.83810002 0.67629999 0.83810002 0.67479998 0.8211 0.67400002 0.82620001
		 0.67909998 0.80500001 0.67659998 0.80549997 0.6767 0.83520001 0.67900002 0.8355 0.68190002
		 0.7938 0.68099999 0.83710003 0.6807 0.80309999 0.6803 0.83579999 0.67309999 0.79390001
		 0.67400002 0.83679998 0.67019999 0.82239997 0.6692 0.82450002 0.67009997 0.89740002
		 0.66979998 0.89749998 0.67019999 0.8976 0.66839999 0.89749998 0.6688 0.89749998 0.68400002
		 0.89749998 0.68370003 0.89749998 0.68279999 0.89749998 0.68239999 0.89749998 0.67439997
		 0.89749998 0.67949998 0.89749998 0.66939998 0.89749998 0.67360002 0.8976 0.6735 0.89749998
		 0.6814 0.8976 0.68169999 0.89749998 0.68360001 0.89749998 0.6832 0.89749998 0.68599999
		 0.89749998 0.68610001 0.89749998 0.6663 0.89749998 0.66640002 0.89749998 0.66820002
		 0.89749998 0.66860002 0.89749998 0.67409998 0.80199999 0.67460001 0.83560002 0.66839999
		 0.89749998 0.68400002 0.89749998 0.68239999 0.89749998 0.67949998 0.89749998 0.67439997
		 0.89749998 0.66979998 0.89749998 0.66979998 0.89749998;
	setAttr ".cuvs" -type "string" "map1";
	setAttr ".dcc" -type "string" "Ambient+Diffuse";
	setAttr -s 32 ".vt[0:31]"  709.89794922 -0.85606003 403.45678711 712.40136719 -0.85606003 403.3203125
		 711.74511719 1.045180321 402.76928711 710.38330078 1.033650398 402.8840332 711.13916016 -0.85606003 396.35058594
		 709.088867188 -0.85606003 396.36694336 709.51806641 1.16222 397.014892578 710.89501953 1.16090965 396.99804688
		 710.33496094 1.23863029 402.7434082 711.72607422 1.23863029 402.62060547 712.2734375 1.28619003 401.44506836
		 708.81103516 1.28619003 401.60888672 707.42578125 -0.80362988 398.75366211 707.83349609 -0.91954041 401.97900391
		 708.58837891 1.082650185 401.65332031 708.1796875 1.19159031 398.97827148 712.28369141 1.40209961 399.036376953
		 708.40625 1.40209961 399.00024414063 713.30761719 -0.91954994 401.74804688 713.22802734 -0.80362988 398.79077148
		 712.50976563 1.19134045 399.011474609 712.50488281 1.082449913 401.46240234 709.65869141 -0.85606003 403.38476563
		 710.14355469 1.033479691 402.81689453 712.60058594 -0.85606003 403.2175293 711.94433594 1.033040047 402.66455078
		 708.89404297 -0.85606003 396.47192383 709.32226563 1.1239996 397.11132813 710.93310547 1.34967995 397.14794922
		 709.5234375 1.34967995 397.16577148 711.11669922 1.12485027 397.083251953 711.36230469 -0.85606003 396.44482422;
	setAttr -s 58 ".ed[0:57]"  0 1 0 1 2 1 2 3 1 3 0 1 4 5 0 5 6 1 6 7 1
		 7 4 1 8 9 0 9 10 0 10 11 1 11 8 0 12 13 0 13 14 0 14 15 1 15 12 0 16 17 1 17 11 0
		 10 16 0 18 19 0 19 20 0 20 21 1 21 18 1 13 22 0 22 23 1 23 14 1 24 18 0 21 25 1 25 24 0
		 26 12 0 15 27 1 27 26 1 28 29 0 29 17 0 16 28 0 30 7 1 7 28 1 28 30 1 6 27 1 27 29 1
		 29 6 1 23 3 1 3 8 1 8 23 1 2 25 1 25 9 1 9 2 1 10 21 1 20 16 1 20 30 1 15 17 0 14 11 0
		 1 24 0 22 0 0 5 26 0 30 31 1 31 4 0 19 31 0;
	setAttr -s 48 ".n[0:47]" -type "float3"  1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20;
	setAttr -s 27 -ch 104 ".fc[0:26]" -type "polyFaces" 
		f 4 0 1 2 3
		mu 0 4 0 1 2 3
		f 4 4 5 6 7
		mu 0 4 4 5 6 7
		f 4 8 9 10 11
		mu 0 4 8 9 10 11
		f 4 12 13 14 15
		mu 0 4 12 13 14 15
		f 4 16 17 -11 18
		mu 0 4 16 17 11 10
		f 4 19 20 21 22
		mu 0 4 18 19 20 21
		f 4 23 24 25 -14
		mu 0 4 13 22 23 14
		f 4 26 -23 27 28
		mu 0 4 24 18 21 25
		f 4 29 -16 30 31
		mu 0 4 26 12 15 27
		f 4 32 33 -17 34
		mu 0 4 28 29 17 16
		f 3 35 36 37
		mu 0 3 30 31 32
		f 3 38 39 40
		mu 0 3 33 56 34
		f 3 41 42 43
		mu 0 3 35 57 36
		f 3 44 45 46
		mu 0 3 37 38 58
		f 4 -19 47 -22 48
		mu 0 4 39 40 59 60
		f 4 -35 -49 49 -38
		mu 0 4 61 39 60 62
		f 4 -33 -37 -7 -41
		mu 0 4 34 61 41 33
		f 4 -34 -40 -31 50
		mu 0 4 42 34 56 43
		f 4 -18 -51 -15 51
		mu 0 4 44 42 43 45
		f 4 -12 -52 -26 -44
		mu 0 4 36 44 45 35
		f 4 -9 -43 -3 -47
		mu 0 4 58 36 57 37
		f 4 -10 -46 -28 -48
		mu 0 4 40 58 38 59
		f 4 -2 52 -29 -45
		mu 0 4 37 46 47 38
		f 4 -4 -42 -25 53
		mu 0 4 48 57 35 49
		f 4 -6 54 -32 -39
		mu 0 4 33 50 51 56
		f 4 -8 -36 55 56
		mu 0 4 52 41 62 53
		f 4 57 -56 -50 -21
		mu 0 4 19 54 55 20;
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
connectAttr "Rock_1_8Shape.iog" "aiStandardSurface1SG.dsm" -na;
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
// End of Rock_1_8.ma
