//Maya ASCII 2023 scene
//Name: Roadstones_1_5.ma
//Last modified: Mon, Aug 01, 2022 04:24:02 PM
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
fileInfo "UUID" "7DF7B984-4117-79B4-3C5B-EC88A4E1BFAA";
createNode transform -n "Roadstones_1_5";
	rename -uid "121D5C14-4096-E65F-90BE-B29FCC772C41";
	setAttr ".t" -type "double3" -600.26025390625 0.14993000030517578 -264.055908203125 ;
	setAttr ".rp" -type "double3" 600.26025390625 -0.14993000030517578 264.055908203125 ;
	setAttr ".sp" -type "double3" 600.26025390625 -0.14993000030517578 264.055908203125 ;
createNode mesh -n "Roadstones_1_5Shape" -p "Roadstones_1_5";
	rename -uid "A8419954-4B6C-EBD4-8AE5-BDB90F33DF80";
	setAttr -k off ".v";
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".uvst[0].uvsn" -type "string" "map1";
	setAttr -s 40 ".uvst[0].uvsp[0:39]" -type "float2" 0.67580003 0.72659999
		 0.6803 0.72659999 0.68000001 0.8247 0.67619997 0.8247 0.67619997 0.84130001 0.67989999
		 0.84130001 0.68049997 0.72659999 0.68010002 0.8258 0.67570001 0.72659999 0.676 0.8258
		 0.676 0.884 0.67619997 0.88279998 0.67619997 0.90109998 0.68000001 0.88279998 0.68010002
		 0.884 0.67989999 0.90109998 0.68049997 0.78479999 0.6803 0.78479999 0.67570001 0.78479999
		 0.67580003 0.78479999 0.67989999 0.84130001 0.67619997 0.84130001 0.68049997 0.72659999
		 0.68010002 0.8258 0.6803 0.72659999 0.67580003 0.72659999 0.67619997 0.8247 0.68000001
		 0.8247 0.67570001 0.72659999 0.676 0.8258 0.676 0.884 0.67619997 0.90109998 0.67619997
		 0.88279998 0.68010002 0.884 0.68000001 0.88279998 0.67989999 0.90109998 0.6803 0.78479999
		 0.68049997 0.78479999 0.67570001 0.78479999 0.67580003 0.78479999;
	setAttr ".cuvs" -type "string" "map1";
	setAttr ".dcc" -type "string" "Ambient+Diffuse";
	setAttr -s 20 ".vt[0:19]"  595.61865234 -0.14991999 266.75024414 604.89501953 -0.14991999 267.56811523
		 604.14160156 1.36923027 267.030517578 596.37207031 1.36923027 266.34570313 596.48535156 1.65182018 265.97094727
		 604.03515625 1.65182018 266.63671875 604.03515625 1.65182018 261.47509766 596.48535156 1.65182018 262.14086914
		 605.22509766 -0.14991999 267.28686523 605.22509766 -0.14993 260.82495117 604.46240234 1.38685989 261.36865234
		 604.46240234 1.38685989 266.74316406 604.89501953 -0.14993 260.54370117 595.61865234 -0.14993 261.36157227
		 596.37207031 1.36923027 261.76635742 604.14160156 1.36923027 261.081298828 595.29541016 -0.14993 261.6940918
		 595.29541016 -0.14991999 266.41772461 596.058105469 1.38685989 266.0083007813 596.058105469 1.38685989 262.10351563;
	setAttr -s 36 ".ed[0:35]"  0 1 0 1 2 0 2 3 0 3 0 0 4 5 0 5 6 0 6 7 0
		 7 4 0 8 9 0 9 10 0 10 11 0 11 8 0 12 13 0 13 14 0 14 15 0 15 12 0 16 17 0 17 18 0
		 18 19 0 19 16 0 18 3 1 3 4 1 4 18 1 2 11 1 11 5 1 5 2 1 19 7 1 7 14 1 14 19 1 10 15 1
		 15 6 1 6 10 1 1 8 0 17 0 0 9 12 0 13 16 0;
	setAttr -s 40 ".n[0:39]" -type "float3"  1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20;
	setAttr -s 17 -ch 64 ".fc[0:16]" -type "polyFaces" 
		f 4 0 1 2 3
		mu 0 4 0 1 2 3
		f 4 4 5 6 7
		mu 0 4 4 5 20 21
		f 4 8 9 10 11
		mu 0 4 6 22 7 23
		f 4 12 13 14 15
		mu 0 4 24 25 26 27
		f 4 16 17 18 19
		mu 0 4 8 28 9 29
		f 3 20 21 22
		mu 0 3 10 11 12
		f 3 23 24 25
		mu 0 3 13 14 15
		f 3 26 27 28
		mu 0 3 30 31 32
		f 3 29 30 31
		mu 0 3 33 34 35
		f 4 -8 -27 -19 -23
		mu 0 4 12 31 30 10
		f 4 -5 -22 -3 -26
		mu 0 4 15 12 11 13
		f 4 -6 -25 -11 -32
		mu 0 4 35 15 14 33
		f 4 -7 -31 -15 -28
		mu 0 4 31 35 34 32
		f 4 -12 -24 -2 32
		mu 0 4 16 14 13 17
		f 4 -18 33 -4 -21
		mu 0 4 10 18 19 11
		f 4 -16 -30 -10 34
		mu 0 4 36 34 33 37
		f 4 -20 -29 -14 35
		mu 0 4 38 30 32 39;
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
connectAttr "Roadstones_1_5Shape.iog" "aiStandardSurface1SG.dsm" -na;
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
// End of Roadstones_1_5.ma
