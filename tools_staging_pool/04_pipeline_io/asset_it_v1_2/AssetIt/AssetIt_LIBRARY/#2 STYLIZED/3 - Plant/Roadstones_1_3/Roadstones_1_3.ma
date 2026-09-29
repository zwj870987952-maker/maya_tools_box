//Maya ASCII 2023 scene
//Name: Roadstones_1_3.ma
//Last modified: Mon, Aug 01, 2022 04:24:58 PM
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
fileInfo "UUID" "8BDF0F11-4730-F3B2-A94E-D99999A01CD3";
createNode transform -n "Roadstones_1_3";
	rename -uid "855D9661-40F3-92EE-C793-58973CBBFE47";
	setAttr ".t" -type "double3" -588.25048828125 0.14993000030517578 -278.237060546875 ;
	setAttr ".rp" -type "double3" 588.25048828125 -0.14993000030517578 278.237060546875 ;
	setAttr ".sp" -type "double3" 588.25048828125 -0.14993000030517578 278.237060546875 ;
createNode mesh -n "Roadstones_1_3Shape" -p "Roadstones_1_3";
	rename -uid "6494AB84-4590-1038-FAAA-098D7C92C75C";
	setAttr -k off ".v";
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".uvst[0].uvsn" -type "string" "map1";
	setAttr -s 61 ".uvst[0].uvsp[0:60]" -type "float2" 0.67540002 0.72659999
		 0.67510003 0.72659999 0.6749 0.82499999 0.67510003 0.82499999 0.67369998 0.72659999
		 0.67199999 0.72659999 0.67229998 0.82609999 0.67360002 0.82609999 0.67220002 0.72659999
		 0.67189997 0.72659999 0.67220002 0.82459998 0.6724 0.82459998 0.67229998 0.81470001
		 0.67330003 0.81470001 0.67369998 0.81470001 0.67259997 0.81470001 0.6749 0.81470001
		 0.67470002 0.81470001 0.67360002 0.81470001 0.6749 0.72659999 0.67470002 0.82609999
		 0.67320001 0.72659999 0.67470002 0.82590002 0.67330003 0.82590002 0.67229998 0.82590002
		 0.67229998 0.88410002 0.67229998 0.90109998 0.67220002 0.88270003 0.67470002 0.88410002
		 0.6749 0.88309997 0.67470002 0.90109998 0.67229998 0.88429999 0.67470002 0.88429999
		 0.67259997 0.90109998 0.6724 0.88270003 0.67330003 0.90109998 0.67330003 0.88410002
		 0.6749 0.90109998 0.67510003 0.88309997 0.67360002 0.90109998 0.67360002 0.88429999
		 0.67199999 0.78479999 0.67189997 0.78479999 0.67510003 0.78479999 0.6749 0.78479999
		 0.67510003 0.72659999 0.6749 0.82499999 0.67470002 0.81470001 0.67229998 0.81470001
		 0.67189997 0.72659999 0.67220002 0.82459998 0.6749 0.72659999 0.67199999 0.72659999
		 0.67220002 0.88270003 0.67229998 0.90109998 0.67470002 0.90109998 0.6749 0.88309997
		 0.67189997 0.78479999 0.67199999 0.78479999 0.67510003 0.78479999 0.6749 0.78479999;
	setAttr ".cuvs" -type "string" "map1";
	setAttr ".dcc" -type "string" "Ambient+Diffuse";
	setAttr -s 33 ".vt[0:32]"  591.79638672 -0.14991999 278.48022461 591.2734375 -0.14993 273.76342773
		 590.80273438 1.37370968 274.50195313 591.24121094 1.37370968 278.45214844 588.32128906 -0.14993 272.75024414
		 584.96582031 -0.14993 273.38793945 585.50195313 1.39179993 274.13525391 588.29443359 1.39179993 273.60449219
		 585.22705078 -0.14991999 278.48022461 584.71240234 -0.14991999 282.19604492 585.24023438 1.36771011 281.5559082
		 585.66992188 1.36771965 278.45214844 591.28076172 -0.14991999 282.20629883 590.81054688 1.37372017 281.56347656
		 585.62255859 1.65182018 281.56225586 587.60205078 1.65182018 282.43457031 588.37207031 1.65182018 278.65722656
		 586.050292969 1.65182018 278.47094727 590.84130859 1.65182018 278.46948242 590.40722656 1.65182018 274.55395508
		 588.29541016 1.65182018 274.051269531 590.41552734 1.65182018 281.5480957 585.61669922 1.65182018 274.56005859
		 584.70458984 -0.14993 273.77319336 585.23242188 1.36771965 274.50878906 590.94628906 -0.14993 273.37524414
		 590.47021484 1.39179993 274.12231445 587.40429688 -0.14991999 283.72387695 590.95263672 -0.14991999 282.60668945
		 590.47753906 1.3883791 281.95776367 587.51855469 1.38844013 282.8894043 584.94091797 -0.14991999 282.63720703
		 585.47607422 1.38850021 281.98852539;
	setAttr -s 60 ".ed[0:59]"  0 1 0 1 2 0 2 3 0 3 0 1 4 5 0 5 6 0 6 7 0
		 7 4 1 8 9 0 9 10 0 10 11 0 11 8 1 12 0 0 3 13 0 13 12 1 14 15 0 15 16 1 16 17 1 17 14 0
		 16 18 1 18 19 0 19 20 0 20 16 1 15 21 0 21 18 0 20 22 0 22 17 0 23 8 0 11 24 0 24 23 0
		 25 4 0 7 26 0 26 25 0 27 28 0 28 29 1 29 30 0 30 27 0 31 27 0 30 32 0 32 31 0 32 14 1
		 14 10 1 10 32 1 29 13 1 13 21 1 21 29 1 24 22 1 22 6 1 6 24 1 26 19 1 19 2 1 2 26 1
		 11 17 1 15 30 1 3 18 1 20 7 1 5 23 0 28 12 0 9 31 0 1 25 0;
	setAttr -s 59 ".n[0:58]" -type "float3"  1e+20 1e+20 1e+20 1e+20 1e+20
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
		 1e+20 1e+20 1e+20 1e+20;
	setAttr -s 28 -ch 108 ".fc[0:27]" -type "polyFaces" 
		f 4 0 1 2 3
		mu 0 4 0 1 2 3
		f 4 4 5 6 7
		mu 0 4 4 5 6 7
		f 4 8 9 10 11
		mu 0 4 8 9 10 11
		f 4 12 -4 13 14
		mu 0 4 45 0 3 46
		f 4 15 16 17 18
		mu 0 4 12 13 14 15
		f 4 19 20 21 22
		mu 0 4 14 16 17 18
		f 4 23 24 -20 -17
		mu 0 4 13 47 16 14
		f 4 -18 -23 25 26
		mu 0 4 15 14 18 48
		f 4 27 -12 28 29
		mu 0 4 49 8 11 50
		f 4 30 -8 31 32
		mu 0 4 19 4 7 20
		f 4 33 34 35 36
		mu 0 4 21 51 22 23
		f 4 37 -37 38 39
		mu 0 4 52 21 23 24
		f 3 40 41 42
		mu 0 3 25 26 27
		f 3 43 44 45
		mu 0 3 28 29 30
		f 3 46 47 48
		mu 0 3 53 54 31
		f 3 49 50 51
		mu 0 3 32 55 56
		f 4 -27 -47 -29 52
		mu 0 4 33 54 53 34
		f 4 -24 53 -36 -46
		mu 0 4 30 35 36 28
		f 4 -25 -45 -14 54
		mu 0 4 37 30 29 38
		f 4 -26 55 -7 -48
		mu 0 4 54 39 40 31
		f 4 -16 -41 -39 -54
		mu 0 4 35 26 25 36
		f 4 -22 -50 -32 -56
		mu 0 4 39 55 32 40
		f 4 -19 -53 -11 -42
		mu 0 4 26 33 34 27
		f 4 -21 -55 -3 -51
		mu 0 4 55 37 38 56
		f 4 -6 56 -30 -49
		mu 0 4 31 41 42 53
		f 4 -15 -44 -35 57
		mu 0 4 43 29 28 44
		f 4 -10 58 -40 -43
		mu 0 4 27 57 58 25
		f 4 -2 59 -33 -52
		mu 0 4 56 59 60 32;
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
connectAttr "Roadstones_1_3Shape.iog" "aiStandardSurface1SG.dsm" -na;
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
// End of Roadstones_1_3.ma
