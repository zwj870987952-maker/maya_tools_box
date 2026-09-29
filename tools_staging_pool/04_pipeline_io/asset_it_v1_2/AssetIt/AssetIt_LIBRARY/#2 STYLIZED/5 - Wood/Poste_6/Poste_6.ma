//Maya ASCII 2023 scene
//Name: Poste_6.ma
//Last modified: Mon, Aug 01, 2022 02:10:29 PM
//Codeset: 1252
requires maya "2023";
requires -nodeType "aiStandardSurface" "mtoa" "5.1.0";
requires "stereoCamera" "10.0";
requires "stereoCamera" "10.0";
currentUnit -l centimeter -a degree -t film;
fileInfo "application" "maya";
fileInfo "product" "Maya 2023";
fileInfo "version" "2023";
fileInfo "cutIdentifier" "202202161415-df43006fd3";
fileInfo "osv" "Windows 10 Home v2009 (Build: 19044)";
fileInfo "UUID" "923ECEE8-42C4-7965-29D4-9EA96C501DF1";
createNode transform -n "Poste_6";
	rename -uid "DD9BF109-4CA9-733B-FD09-68B09767B070";
	setAttr ".t" -type "double3" 47.553146362304688 -0.39600992202758789 -255.4783935546875 ;
	setAttr ".rp" -type "double3" -47.553146362304688 0.39600992202758789 255.4783935546875 ;
	setAttr ".sp" -type "double3" -47.553146362304688 0.39600992202758789 255.4783935546875 ;
createNode mesh -n "Poste_6Shape" -p "Poste_6";
	rename -uid "4F95BE3A-4B26-40A6-8981-4F9B63CF3DEF";
	setAttr -k off ".v";
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".uvst[0].uvsn" -type "string" "map1";
	setAttr -s 56 ".uvst[0].uvsp[0:55]" -type "float2" 0.085900001 0.7044
		 0.092600003 0.7044 0.092600003 0.78079998 0.085900001 0.78079998 0.093500003 0.7044
		 0.093500003 0.78079998 0.085000001 0.7044 0.085000001 0.78079998 0.092600003 0.80479997
		 0.092600003 0.75019997 0.093500003 0.75019997 0.093500003 0.80479997 0.085000001
		 0.75019997 0.085000001 0.80479997 0.085900001 0.80479997 0.085900001 0.75019997 0.1077
		 0.73869997 0.067199998 0.73869997 0.1034 0.73869997 0.071500003 0.73869997 0.093500003
		 0.7044 0.093500003 0.78079998 0.085000001 0.7044 0.085000001 0.78079998 0.092600003
		 0.75019997 0.092600003 0.80479997 0.093500003 0.80479997 0.093500003 0.75019997 0.085000001
		 0.80479997 0.085000001 0.75019997 0.085900001 0.75019997 0.085900001 0.80479997 0.092600003
		 0.7044 0.085900001 0.7044 0.085900001 0.78079998 0.092600003 0.78079998 0.067199998
		 0.73869997 0.1077 0.73869997 0.071500003 0.73869997 0.1034 0.73869997 0.093500003
		 0.80479997 0.092600003 0.80479997 0.092600003 0.80479997 0.093500003 0.80479997 0.085900001
		 0.78079998 0.092600003 0.78079998 0.093500003 0.78079998 0.093500003 0.78079998 0.085000001
		 0.80479997 0.085900001 0.80479997 0.085000001 0.78079998 0.085000001 0.78079998 0.085900001
		 0.80479997 0.085000001 0.80479997 0.092600003 0.78079998 0.085900001 0.78079998;
	setAttr ".cuvs" -type "string" "map1";
	setAttr ".dcc" -type "string" "Ambient+Diffuse";
	setAttr -s 24 ".vt[0:23]"  -49.072296143 0.39600992 257.40454102 -46.033996582 0.39600992 257.40454102
		 -46.033996582 41.53289795 257.40454102 -49.072296143 41.53289795 257.40454102 -45.62695313 0.39600992 256.99755859
		 -45.62695313 0.39600992 253.95922852 -45.62695313 41.53289795 253.95922852 -45.62695313 41.53289795 256.99755859
		 -49.4793396 0.39600992 253.95922852 -49.4793396 0.39600992 256.99755859 -49.4793396 41.53289795 256.99755859
		 -49.4793396 41.53289795 253.95922852 -46.033996582 0.39600992 253.55224609 -46.033996582 41.53289795 253.55224609
		 -49.072296143 41.53289795 253.55224609 -49.072296143 0.39600992 253.55224609 -46.068267822 41.90002441 254.30737305
		 -49.038024902 41.90002441 254.30737305 -49.038024902 41.90002441 256.6496582 -46.068267822 41.90002441 256.6496582
		 -46.38208008 41.90002441 253.99365234 -48.72421265 41.90002441 253.99365234 -48.72421265 41.90002441 256.96337891
		 -46.38208008 41.90002441 256.96337891;
	setAttr -s 42 ".ed[0:41]"  0 1 0 1 2 0 2 3 0 3 0 0 4 5 0 5 6 0 6 7 0
		 7 4 0 8 9 0 9 10 0 10 11 0 11 8 0 1 4 0 7 2 0 12 13 0 13 6 0 5 12 0 11 14 0 14 15 0
		 15 8 0 9 0 0 3 10 0 12 15 0 14 13 0 16 17 1 17 18 0 18 19 1 19 16 0 16 20 0 20 21 0
		 21 17 0 18 22 0 22 23 0 23 19 0 7 19 1 23 2 1 13 20 1 16 6 1 14 21 1 11 17 1 10 18 1
		 3 22 1;
	setAttr -s 56 ".n[0:55]" -type "float3"  1e+20 1e+20 1e+20 1e+20 1e+20
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
	setAttr -s 19 -ch 76 ".fc[0:18]" -type "polyFaces" 
		f 4 0 1 2 3
		mu 0 4 0 1 2 3
		f 4 4 5 6 7
		mu 0 4 4 20 5 21
		f 4 8 9 10 11
		mu 0 4 6 22 7 23
		f 4 -2 12 -8 13
		mu 0 4 8 9 10 11
		f 4 14 15 -6 16
		mu 0 4 24 25 26 27
		f 4 -12 17 18 19
		mu 0 4 12 13 14 15
		f 4 -10 20 -4 21
		mu 0 4 28 29 30 31
		f 4 22 -19 23 -15
		mu 0 4 32 33 34 35
		f 4 24 25 26 27
		mu 0 4 16 17 36 37
		f 4 28 29 30 -25
		mu 0 4 16 18 19 17
		f 4 31 32 33 -27
		mu 0 4 36 38 39 37
		f 4 -14 34 -34 35
		mu 0 4 8 11 40 41
		f 4 -16 36 -29 37
		mu 0 4 26 25 42 43
		f 4 -24 38 -30 -37
		mu 0 4 35 34 44 45
		f 4 -7 -38 -28 -35
		mu 0 4 21 5 46 47
		f 4 -18 39 -31 -39
		mu 0 4 14 13 48 49
		f 4 -11 40 -26 -40
		mu 0 4 23 7 50 51
		f 4 -22 41 -32 -41
		mu 0 4 28 31 52 53
		f 4 -3 -36 -33 -42
		mu 0 4 3 2 54 55;
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
	rename -uid "8452FADB-4F52-AA99-C07F-C98BBF23517B";
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
	setAttr ".msaa" yes;
	setAttr ".aasc" 16;
	setAttr ".laa" yes;
	setAttr ".fprt" yes;
select -ne :renderPartition;
	setAttr -s 4 ".st";
select -ne :renderGlobalsList1;
select -ne :defaultShaderList1;
	setAttr -s 10 ".s";
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
select -ne :ikSystem;
	setAttr -s 4 ".sol";
connectAttr "aiStandardSurface1SG.msg" "materialInfo1.sg";
connectAttr "Toon_shd.msg" "materialInfo1.m";
connectAttr "Toon_shd.msg" "materialInfo1.t" -na;
connectAttr "Toon_shd.out" "aiStandardSurface1SG.ss";
connectAttr "Poste_6Shape.iog" "aiStandardSurface1SG.dsm" -na;
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
// End of Poste_6.ma
