//Maya ASCII 2023 scene
//Name: Ingot_1_1.ma
//Last modified: Fri, Aug 05, 2022 06:45:18 PM
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
fileInfo "UUID" "36ED74FA-4958-AE5D-1094-088246E3B5B2";
createNode transform -n "Ingot_1_1";
	rename -uid "3FF5F4A2-45AD-0016-8558-5A86491CA4F3";
	setAttr ".t" -type "double3" 460.58447265625 -4.6304283142089844 -405.966552734375 ;
	setAttr ".rp" -type "double3" -460.58447265625 4.6304283142089844 405.966552734375 ;
	setAttr ".sp" -type "double3" -460.58447265625 4.6304283142089844 405.966552734375 ;
createNode mesh -n "Ingot_1_1Shape" -p "Ingot_1_1";
	rename -uid "2621564B-44B6-D6F3-0B0A-8D811F844B55";
	setAttr -k off ".v";
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".uvst[0].uvsn" -type "string" "map1";
	setAttr -s 56 ".uvst[0].uvsp[0:55]" -type "float2" 0.97589999 0.068999998
		 0.97219998 0.1776 0.95910001 0.1776 0.95539999 0.068999998 0.97649997 0.19670001
		 0.96740001 0.19670001 0.96960002 0.1917 0.97420001 0.1917 0.97649997 0.1296 0.97420001
		 0.1346 0.96740001 0.1296 0.96960002 0.1346 0.96329999 0.17910001 0.96799999 0.17910001
		 0.9673 0.16869999 0.96399999 0.16869999 0.95590001 0.1591 0.95959997 0.26730001 0.97180003
		 0.26730001 0.97539997 0.1591 0.9673 0.12530001 0.96399999 0.12530001 0.95569998 0.15350001
		 0.95539999 0.15889999 0.95969999 0.2728 0.95910001 0.26750001 0.9756 0.15350001 0.97589999
		 0.15889999 0.9716 0.2728 0.97219998 0.26750001 0.96329999 0.26899999 0.96799999 0.26899999
		 0.96869999 0.2728 0.96270001 0.2728 0.95910001 0.1776 0.95539999 0.068999998 0.97589999
		 0.068999998 0.97219998 0.1776 0.96799999 0.17910001 0.96329999 0.17910001 0.96399999
		 0.16869999 0.9673 0.16869999 0.96399999 0.12530001 0.9673 0.12530001 0.95569998 0.15350001
		 0.95539999 0.15889999 0.95969999 0.2728 0.95910001 0.26750001 0.9756 0.15350001 0.97589999
		 0.15889999 0.9716 0.2728 0.97219998 0.26750001 0.96799999 0.26899999 0.96869999 0.2728
		 0.96329999 0.26899999 0.96270001 0.2728;
	setAttr ".cuvs" -type "string" "map1";
	setAttr ".dcc" -type "string" "Ambient+Diffuse";
	setAttr -s 32 ".vt[0:31]"  -459.26611328 4.6843605 408.86010742 -459.734375 5.77396011 408.57885742
		 -461.43457031 5.77396011 408.57885742 -461.90283203 4.6843605 408.86010742 -459.81542969 5.82788849 403.42529297
		 -461.35351563 5.82788849 403.42529297 -460.97119141 5.82788849 403.80786133 -460.19775391 5.82788849 403.80786133
		 -459.81542969 5.82789993 408.50732422 -460.19775391 5.82789993 408.12475586 -461.35351563 5.82789993 408.50732422
		 -460.97119141 5.82789993 408.12475586 -461.43457031 5.77399063 403.4128418 -461.90283203 4.68432999 403.1315918
		 -460.8828125 5.7892189 408.015869141 -460.28613281 5.7892189 408.015869141 -460.36816406 5.68534851 407.87817383
		 -460.80078125 5.68534851 407.87817383 -459.26611328 4.68432999 403.1315918 -459.734375 5.77399063 403.4128418
		 -461.83935547 4.68632126 403.072998047 -461.37304688 5.77199936 403.35302734 -459.79589844 5.77199936 403.35302734
		 -459.32958984 4.68632126 403.072998047 -460.28613281 5.7892189 403.91674805 -460.8828125 5.7892189 403.91674805
		 -460.80078125 5.68534851 404.054199219 -460.36816406 5.68534851 404.054199219 -461.86816406 4.63042831 403.11621094
		 -459.30078125 4.63042831 403.11621094 -461.86816406 4.63042831 408.81640625 -459.30078125 4.63042831 408.81640625;
	setAttr -s 62 ".ed[0:61]"  0 1 0 1 2 0 2 3 0 3 0 0 4 5 0 5 6 1 6 7 1
		 7 4 1 8 4 0 7 9 1 9 8 1 5 10 0 10 11 1 11 6 1 2 12 0 12 13 0 13 3 0 14 15 1 15 16 0
		 16 17 0 17 14 0 18 19 0 19 1 0 0 18 0 10 8 0 9 11 1 20 21 0 21 22 0 22 23 0 23 20 0
		 24 25 1 25 26 0 26 27 0 27 24 0 26 17 0 16 27 0 15 24 1 25 14 1 28 13 0 13 20 0 20 28 0
		 5 21 1 21 12 1 12 5 1 29 23 0 23 18 0 18 29 0 4 19 1 19 22 1 22 4 1 28 30 0 30 3 0
		 2 10 0 29 28 0 31 29 0 0 31 0 8 1 0 30 31 0 24 7 0 6 25 0 15 9 0 11 14 0;
	setAttr -s 88 ".n[0:87]" -type "float3"  1e+20 1e+20 1e+20 1e+20 1e+20
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
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20;
	setAttr -s 32 -ch 124 ".fc[0:31]" -type "polyFaces" 
		f 4 0 1 2 3
		mu 0 4 0 1 2 3
		f 4 4 5 6 7
		mu 0 4 4 5 6 7
		f 4 8 -8 9 10
		mu 0 4 8 4 7 9
		f 4 11 12 13 -6
		mu 0 4 5 10 11 6
		f 4 -3 14 15 16
		mu 0 4 3 2 34 35
		f 4 17 18 19 20
		mu 0 4 12 13 14 15
		f 4 21 22 -1 23
		mu 0 4 36 37 1 0
		f 4 24 -11 25 -13
		mu 0 4 10 8 9 11
		f 4 26 27 28 29
		mu 0 4 16 17 18 19
		f 4 30 31 32 33
		mu 0 4 38 39 40 41
		f 4 -33 34 -20 35
		mu 0 4 20 21 42 43
		f 4 36 -34 -36 -19
		mu 0 4 13 38 41 14
		f 4 37 -21 -35 -32
		mu 0 4 39 12 15 40
		f 3 38 39 40
		mu 0 3 22 23 16
		f 3 41 42 43
		mu 0 3 24 17 25
		f 3 44 45 46
		mu 0 3 26 19 27
		f 3 47 48 49
		mu 0 3 28 29 18
		f 4 50 51 -17 -39
		mu 0 4 22 44 45 23
		f 4 -12 -44 -15 52
		mu 0 4 46 24 25 47
		f 4 -27 -40 -16 -43
		mu 0 4 17 16 23 25
		f 4 53 -41 -30 -45
		mu 0 4 26 22 16 19
		f 4 -5 -50 -28 -42
		mu 0 4 24 28 18 17
		f 4 -22 -46 -29 -49
		mu 0 4 29 27 19 18
		f 4 54 -47 -24 55
		mu 0 4 48 26 27 49
		f 4 -9 56 -23 -48
		mu 0 4 28 50 51 29
		f 4 57 -56 -4 -52
		mu 0 4 44 48 49 45
		f 4 -25 -53 -2 -57
		mu 0 4 50 46 47 51
		f 4 -31 58 -7 59
		mu 0 4 30 31 32 33
		f 4 -37 60 -10 -59
		mu 0 4 31 52 53 32
		f 4 -38 -60 -14 61
		mu 0 4 54 30 33 55
		f 4 -18 -62 -26 -61
		mu 0 4 52 54 55 53
		f 4 -54 -55 -58 -51
		mu 0 4 22 26 48 44;
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
	rename -uid "C00CB98B-4491-B834-CCDB-3EBD6618D1A5";
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
connectAttr "Ingot_1_1Shape.iog" "aiStandardSurface1SG.dsm" -na;
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
// End of Ingot_1_1.ma
