//Maya ASCII 2023 scene
//Name: Rock_1_7.ma
//Last modified: Mon, Aug 01, 2022 04:23:24 PM
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
fileInfo "UUID" "EA3748E3-4181-99AB-F478-E8B3BA3B3875";
createNode transform -n "Rock_1_7";
	rename -uid "8979D788-4917-0D6E-F9DB-3AAA820336B3";
	setAttr ".t" -type "double3" -697.047119140625 0.70687007904052734 -400.9290771484375 ;
	setAttr ".rp" -type "double3" 697.047119140625 -0.70687007904052734 400.9290771484375 ;
	setAttr ".sp" -type "double3" 697.047119140625 -0.70687007904052734 400.9290771484375 ;
createNode mesh -n "Rock_1_7Shape" -p "Rock_1_7";
	rename -uid "CF46A9C1-4CEC-BBA3-31B4-BAABD3C74C0F";
	setAttr -k off ".v";
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".uvst[0].uvsn" -type "string" "map1";
	setAttr -s 81 ".uvst[0].uvsp[0:80]" -type "float2" 0.67449999 0.8351
		 0.67519999 0.86669999 0.67540002 0.86119998 0.67479998 0.83240002 0.67519999 0.83240002
		 0.67570001 0.8581 0.67729998 0.86650002 0.67729998 0.84869999 0.6796 0.83200002 0.67930001
		 0.85399997 0.67940003 0.85659999 0.67970002 0.83340001 0.67729998 0.83819997 0.67729998
		 0.84829998 0.67930001 0.83139998 0.67909998 0.82529998 0.67729998 0.83490002 0.67900002
		 0.82249999 0.67739999 0.78680003 0.67729998 0.86330003 0.67470002 0.838 0.67409998
		 0.78969997 0.67900002 0.85439998 0.67930001 0.83340001 0.67549998 0.8585 0.6749 0.83109999
		 0.67729998 0.88380003 0.6753 0.86870003 0.67970002 0.83950001 0.67940003 0.8646 0.67559999
		 0.82929999 0.67540002 0.83560002 0.67570001 0.8265 0.67430001 0.792 0.67439997 0.79290003
		 0.68059999 0.79220003 0.6807 0.79119998 0.67470002 0.79320002 0.67739999 0.79329997
		 0.6803 0.79250002 0.67390001 0.7902 0.67989999 0.83630002 0.68110001 0.78920001 0.6796
		 0.86189997 0.67860001 0.89819998 0.67879999 0.89819998 0.67470002 0.89829999 0.67439997
		 0.89819998 0.67460001 0.89829999 0.67830002 0.89819998 0.6785 0.89810002 0.67830002
		 0.89810002 0.67500001 0.89819998 0.67470002 0.89819998 0.67919999 0.898 0.67900002
		 0.898 0.67650002 0.89840001 0.67369998 0.898 0.67309999 0.8976 0.67330003 0.8976
		 0.67390001 0.898 0.6749 0.89819998 0.67460001 0.89819998 0.67439997 0.89789999 0.67400002
		 0.8976 0.67369998 0.8976 0.67409998 0.89789999 0.67659998 0.89829999 0.67659998 0.89819998
		 0.67879999 0.89789999 0.67979997 0.8976 0.67949998 0.8976 0.67860001 0.89789999 0.67839998
		 0.89819998 0.67860001 0.89810002 0.68040001 0.8976 0.68019998 0.8976 0.68099999 0.78869998
		 0.67860001 0.89819998 0.67500001 0.89819998 0.67650002 0.89840001;
	setAttr ".cuvs" -type "string" "map1";
	setAttr ".dcc" -type "string" "Ambient+Diffuse";
	setAttr -s 45 ".vt[0:44]"  697.79248047 4.21004868 406.2277832 698.10644531 8.022880554 405.109375
		 695.99658203 8.69949341 404.51733398 695.68261719 4.88666153 405.63574219 692.67578125 4.85280991 404.73632813
		 693.048339844 8.48813629 403.68261719 693.51171875 9.75705719 400.20947266 693.51171875 4.9869194 400.20947266
		 695.53320313 4.61623001 396.29956055 695.41455078 7.59229279 396.72192383 698.090332031 7.86270905 397.056396484
		 698.20849609 4.88666153 396.6340332 697.039550781 10.33917236 400.80029297 700.11279297 9.85151672 401.66259766
		 700.19726563 7.76979065 398.070800781 697.97998047 8.4464035 397.44873047 694.005859375 10.15872192 400.34838867
		 695.3046875 8.17597198 397.11425781 701.61767578 -0.70687008 402.084960938 701.020507813 6.82437134 401.91723633
		 698.43164063 4.45203018 405.92431641 698.19482422 -0.70687008 406.67382813 694.91601563 7.76416016 397.026123047
		 694.95458984 4.87730026 396.58618164 693.32128906 8.42906952 404.18286133 693.0073242188 4.61623001 405.30151367
		 700.51708984 9.40525055 401.77612305 698.75341797 8.059440613 404.88623047 700.72558594 4.47333908 397.79296875
		 700.62792969 7.33196259 398.19677734 696.12988281 9.20690155 404.042724609 698.36035156 8.5302887 404.66870117
		 693.45410156 8.93647003 403.70825195 695.47851563 -0.70687008 406.36352539 692.80322266 -0.30068994 406.029052734
		 695.92529297 -0.62639999 394.90258789 698.60058594 -0.70687008 395.23706055 692.4765625 -0.62639999 405.50073242
		 693.51171875 -0.53641987 400.20947266 695.39550781 -0.62639999 395.12915039 697.58837891 -0.70687008 406.95556641
		 700.31835938 4.21004868 397.22607422 700.71044922 -0.70687008 395.82910156 700.20019531 7.18610382 397.64819336
		 701.083496094 -0.70687008 396.32495117;
	setAttr -s 84 ".ed[0:83]"  0 1 1 1 2 1 2 3 1 3 0 1 4 5 0 5 6 0 6 7 1
		 7 4 1 8 9 0 9 10 1 10 11 1 11 8 1 12 13 0 13 14 1 14 15 1 15 12 1 16 12 0 15 17 1
		 17 16 1 18 19 0 19 20 1 20 21 0 21 18 0 6 22 0 22 23 0 23 7 1 2 24 1 24 25 0 25 3 1
		 19 26 0 26 27 0 27 20 0 28 29 0 29 26 0 19 28 1 30 31 1 31 13 0 12 30 1 32 30 1 16 32 0
		 33 3 1 25 34 0 34 33 0 35 8 1 11 36 1 36 35 0 37 4 0 7 38 1 38 37 0 23 39 0 39 38 0
		 40 0 0 33 40 0 11 41 1 41 42 0 42 36 0 10 43 1 43 41 0 29 43 1 43 14 1 14 29 1 31 1 1
		 1 27 1 27 31 1 17 9 1 9 22 1 22 17 1 32 5 1 5 24 1 24 32 0 28 41 1 26 13 0 40 21 0
		 20 0 1 2 30 1 37 34 0 25 4 1 6 16 0 35 39 0 23 8 1 10 15 1 28 44 0 44 42 0 18 44 0;
	setAttr -s 76 ".n[0:75]" -type "float3"  1e+20 1e+20 1e+20 1e+20 1e+20
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
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20;
	setAttr -s 40 -ch 156 ".fc[0:39]" -type "polyFaces" 
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
		f 4 40 -29 41 42
		mu 0 4 33 3 25 34
		f 4 43 -12 44 45
		mu 0 4 35 8 11 36
		f 4 46 -8 47 48
		mu 0 4 37 4 7 38
		f 4 -48 -26 49 50
		mu 0 4 38 7 23 39
		f 4 51 -4 -41 52
		mu 0 4 40 0 3 33
		f 4 -45 53 54 55
		mu 0 4 36 11 41 42
		f 4 -11 56 57 -54
		mu 0 4 11 10 43 41
		f 3 58 59 60
		mu 0 3 44 45 78
		f 3 61 62 63
		mu 0 3 46 47 48
		f 3 64 65 66
		mu 0 3 49 50 51
		f 3 67 68 69
		mu 0 3 52 79 53
		f 4 -58 -59 -33 70
		mu 0 4 54 45 44 55
		f 4 -37 -64 -31 71
		mu 0 4 56 46 48 80
		f 4 -52 72 -22 73
		mu 0 4 57 58 59 60
		f 4 -39 -70 -27 74
		mu 0 4 61 52 53 62
		f 4 -47 75 -42 76
		mu 0 4 63 64 65 66
		f 4 -19 -67 -24 77
		mu 0 4 67 49 51 68
		f 4 -44 78 -50 79
		mu 0 4 69 70 71 72
		f 4 -15 -60 -57 80
		mu 0 4 73 78 45 74
		f 4 -55 -71 81 82
		mu 0 4 75 54 55 76
		f 4 -14 -72 -34 -61
		mu 0 4 78 56 80 44
		f 4 -1 -74 -32 -63
		mu 0 4 47 57 60 48
		f 4 -36 -75 -2 -62
		mu 0 4 46 61 62 47
		f 4 -5 -77 -28 -69
		mu 0 4 79 63 66 53
		f 4 -40 -78 -6 -68
		mu 0 4 52 67 68 79
		f 4 -9 -80 -25 -66
		mu 0 4 50 69 72 51
		f 4 -18 -81 -10 -65
		mu 0 4 49 73 74 50
		f 4 -82 -35 -20 83
		mu 0 4 77 28 19 18;
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
connectAttr "Rock_1_7Shape.iog" "aiStandardSurface1SG.dsm" -na;
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
// End of Rock_1_7.ma
