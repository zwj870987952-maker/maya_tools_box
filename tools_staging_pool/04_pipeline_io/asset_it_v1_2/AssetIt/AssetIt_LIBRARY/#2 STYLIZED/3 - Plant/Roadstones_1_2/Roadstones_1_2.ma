//Maya ASCII 2023 scene
//Name: Roadstones_1_2.ma
//Last modified: Mon, Aug 01, 2022 04:24:44 PM
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
fileInfo "UUID" "7DA67BA3-4374-273C-6E67-48AA4E342CD1";
createNode transform -n "Roadstones_1_2";
	rename -uid "A735721A-4142-FA14-8DB3-03AED4916BA3";
	setAttr ".t" -type "double3" -587.726806640625 0.14993000030517578 -263.65283203125 ;
	setAttr ".rp" -type "double3" 587.726806640625 -0.14993000030517578 263.65283203125 ;
	setAttr ".sp" -type "double3" 587.726806640625 -0.14993000030517578 263.65283203125 ;
createNode mesh -n "Roadstones_1_2Shape" -p "Roadstones_1_2";
	rename -uid "94BBAB03-4FE2-7415-BD7B-9EA7FC02172F";
	setAttr -k off ".v";
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".uvst[0].uvsn" -type "string" "map1";
	setAttr -s 45 ".uvst[0].uvsp[0:44]" -type "float2" 0.67089999 0.72659999
		 0.67110002 0.8247 0.6735 0.72659999 0.671 0.72659999 0.67129999 0.82590002 0.67330003
		 0.82590002 0.67330003 0.81470001 0.67409998 0.81470001 0.67129999 0.81470001 0.67360002
		 0.72659999 0.67460001 0.72659999 0.67430001 0.82550001 0.67339998 0.82560003 0.67369998
		 0.72659999 0.6735 0.82550001 0.67129999 0.82560003 0.67129999 0.88370001 0.67129999
		 0.90109998 0.67110002 0.8829 0.67129999 0.88410002 0.67330003 0.88410002 0.67330003
		 0.90109998 0.6735 0.88370001 0.67409998 0.90109998 0.67339998 0.88370001 0.67430001
		 0.88370001 0.671 0.78479999 0.67089999 0.78479999 0.67369998 0.78479999 0.6735 0.78479999
		 0.67089999 0.72659999 0.67110002 0.8247 0.67129999 0.81470001 0.67330003 0.81470001
		 0.67129999 0.81470001 0.67089999 0.72659999 0.67110002 0.8247 0.671 0.72659999 0.67110002
		 0.8829 0.67129999 0.90109998 0.67129999 0.90109998 0.67110002 0.8829 0.67330003 0.90109998
		 0.67089999 0.78479999 0.671 0.78479999;
	setAttr ".cuvs" -type "string" "map1";
	setAttr ".dcc" -type "string" "Ambient+Diffuse";
	setAttr -s 24 ".vt[0:23]"  583.93310547 -0.14991999 263.44604492 583.93310547 -0.14991999 267.8137207
		 584.42138672 1.37022972 267.11450195 584.42138672 1.37022972 263.45922852 589.19140625 -0.14993 257.78295898
		 584.22509766 -0.14993 258.99316406 584.71923828 1.38831997 259.67993164 588.83105469 1.38831997 258.67797852
		 588.87646484 1.65182018 268.090820313 590.42089844 1.65182018 263.4375 584.80761719 1.65182018 263.46044922
		 584.80761719 1.65182018 267.076660156 589.49365234 -0.14991999 269.52270508 591.52050781 -0.14991999 263.41503906
		 590.85107422 1.3822403 263.43310547 589.13427734 1.38267994 268.60522461 588.8828125 1.65182018 259.1081543
		 584.80761719 1.65182018 260.10107422 589.6015625 -0.14993 258.013183594 589.24267578 1.38210964 258.90454102
		 583.93310547 -0.14993 259.38574219 584.42138672 1.37022972 260.064208984 584.22460938 -0.14991999 268.20922852
		 584.71679688 1.38296032 267.50415039;
	setAttr -s 43 ".ed[0:42]"  0 1 0 1 2 0 2 3 0 3 0 1 4 5 0 5 6 0 6 7 0
		 7 4 0 8 9 0 9 10 1 10 11 0 11 8 0 12 13 0 13 14 0 14 15 0 15 12 0 9 16 0 16 17 0
		 17 10 0 13 18 0 18 19 0 19 14 0 20 0 0 3 21 0 21 20 0 22 12 0 15 23 0 23 22 0 23 11 1
		 11 2 1 2 23 1 21 17 1 17 6 1 6 21 1 7 16 1 16 19 1 19 7 1 3 10 1 8 15 0 14 9 1 5 20 0
		 1 22 0 18 4 0;
	setAttr -s 51 ".n[0:50]" -type "float3"  1e+20 1e+20 1e+20 1e+20 1e+20
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
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20;
	setAttr -s 20 -ch 77 ".fc[0:19]" -type "polyFaces" 
		f 4 0 1 2 3
		mu 0 4 0 30 1 31
		f 4 4 5 6 7
		mu 0 4 2 3 4 5
		f 4 8 9 10 11
		mu 0 4 6 7 8 32
		f 4 12 13 14 15
		mu 0 4 9 10 11 12
		f 4 -10 16 17 18
		mu 0 4 8 7 33 34
		f 4 19 20 21 -14
		mu 0 4 10 13 14 11
		f 4 22 -4 23 24
		mu 0 4 35 0 31 36
		f 4 25 -16 26 27
		mu 0 4 37 9 12 15
		f 3 28 29 30
		mu 0 3 16 17 18
		f 3 31 32 33
		mu 0 3 38 39 19
		f 3 34 35 36
		mu 0 3 20 21 22
		f 4 -19 -32 -24 37
		mu 0 4 40 39 38 41
		f 4 -9 38 -15 39
		mu 0 4 23 42 24 25
		f 4 -12 -29 -27 -39
		mu 0 4 42 17 16 24
		f 4 -18 -35 -7 -33
		mu 0 4 39 21 20 19
		f 4 -11 -38 -3 -30
		mu 0 4 17 40 41 18
		f 4 -17 -40 -22 -36
		mu 0 4 21 23 25 22
		f 4 -6 40 -25 -34
		mu 0 4 19 26 27 38
		f 4 -2 41 -28 -31
		mu 0 4 18 43 44 16
		f 4 -21 42 -8 -37
		mu 0 4 22 28 29 20;
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
connectAttr "Roadstones_1_2Shape.iog" "aiStandardSurface1SG.dsm" -na;
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
// End of Roadstones_1_2.ma
