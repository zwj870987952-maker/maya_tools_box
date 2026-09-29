//Maya ASCII 2023 scene
//Name: Rock_2_2.ma
//Last modified: Mon, Aug 01, 2022 04:21:57 PM
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
fileInfo "UUID" "65126A5D-414A-CEEB-BE93-43B59315E707";
createNode transform -n "Rock_2_2";
	rename -uid "F81460C9-4341-DC06-F1CB-3C9602BFD88B";
	setAttr ".t" -type "double3" -614.45361328125 1.2313499450683594 -361.9615478515625 ;
	setAttr ".rp" -type "double3" 614.45361328125 -1.2313499450683594 361.9615478515625 ;
	setAttr ".sp" -type "double3" 614.45361328125 -1.2313499450683594 361.9615478515625 ;
createNode mesh -n "Rock_2_2Shape" -p "Rock_2_2";
	rename -uid "8E550F68-4AA4-1143-088B-C9A158860257";
	setAttr -k off ".v";
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".uvst[0].uvsn" -type "string" "map1";
	setAttr -s 105 ".uvst[0].uvsp[0:104]" -type "float2" 0.56129998 0.81379998
		 0.5614 0.81470001 0.5614 0.82630002 0.5614 0.82499999 0.56129998 0.81840003 0.56129998
		 0.82099998 0.56129998 0.82819998 0.5614 0.8251 0.56129998 0.80949998 0.56129998 0.81120002
		 0.5614 0.80919999 0.5614 0.8089 0.5614 0.81739998 0.5614 0.8179 0.56150001 0.82560003
		 0.56150001 0.83350003 0.56150001 0.83420002 0.56150001 0.81150001 0.5614 0.80940002
		 0.56150001 0.81819999 0.56150001 0.8215 0.56129998 0.80930001 0.56129998 0.81800002
		 0.56129998 0.81349999 0.56129998 0.82440001 0.56150001 0.82489997 0.56150001 0.82880002
		 0.5614 0.83200002 0.5614 0.82389998 0.56150001 0.82450002 0.5614 0.83279997 0.56150001
		 0.83660001 0.5614 0.83539999 0.56150001 0.8071 0.5614 0.8057 0.5614 0.80870003 0.56150001
		 0.80989999 0.56150001 0.83590001 0.5614 0.83170003 0.5614 0.829 0.56150001 0.82499999
		 0.56150001 0.824 0.5614 0.8348 0.56150001 0.82459998 0.5614 0.8247 0.5614 0.80229998
		 0.5614 0.80299997 0.56150001 0.80610001 0.56150001 0.80930001 0.5614 0.8283 0.5614
		 0.8276 0.56150001 0.82810003 0.56150001 0.8028 0.56150001 0.82840002 0.56150001 0.83179998
		 0.56150001 0.83270001 0.56150001 0.8351 0.56150001 0.81440002 0.56150001 0.81400001
		 0.56260002 0.87180001 0.5625 0.87180001 0.5625 0.87150002 0.56260002 0.87150002 0.56300002
		 0.8714 0.56290001 0.87129998 0.56290001 0.87180001 0.56290001 0.87169999 0.56230003
		 0.87120003 0.56239998 0.87129998 0.56230003 0.87190002 0.56169999 0.87199998 0.56169999
		 0.87190002 0.56199998 0.87190002 0.56150001 0.87190002 0.56239998 0.87190002 0.56230003
		 0.87180001 0.56279999 0.87129998 0.56150001 0.87150002 0.56199998 0.87150002 0.56150001
		 0.8714 0.56279999 0.87180001 0.56269997 0.87190002 0.56239998 0.87150002 0.56230003
		 0.87150002 0.56269997 0.87180001 0.56260002 0.87159997 0.5625 0.87159997 0.56279999
		 0.8714 0.56269997 0.8714 0.56300002 0.87150002 0.56300002 0.87159997 0.5618 0.87120003
		 0.56260002 0.87180001 0.56260002 0.87150002 0.56300002 0.8714 0.56290001 0.87180001
		 0.56239998 0.87129998 0.56230003 0.87120003 0.56230003 0.87190002 0.56150001 0.87190002
		 0.56199998 0.87190002 0.56279999 0.87129998 0.56199998 0.87150002 0.56279999 0.87180001
		 0.5618 0.87120003;
	setAttr ".cuvs" -type "string" "map1";
	setAttr ".dcc" -type "string" "Ambient+Diffuse";
	setAttr -s 59 ".vt[0:58]"  612.35253906 -1.23134995 356.73803711 610.296875 -1.23134995 361.26489258
		 609.99609375 3.016910553 362.036865234 611.80908203 2.50144958 358.042724609 618.23486328 2.59308052 358.74926758
		 615.49951172 2.37129021 357.035888672 614.74560547 5.66363907 358.19140625 617.14355469 5.85815811 359.69287109
		 619.57373047 -1.23134995 357.59838867 616.46972656 -1.23134995 355.65307617 618.30371094 -1.23134995 366.63696289
		 619.85253906 -1.23134995 363.011230469 618.51953125 3.21912956 363.59521484 617.15234375 3.63471985 366.79443359
		 609.55322266 3.57033157 366.29174805 609.46386719 6.72441101 366.37841797 609.85644531 6.23894119 362.6315918
		 613.24267578 -1.23134995 368.24853516 617.78125 -1.23134995 367.081787109 616.62988281 3.69248962 367.23925781
		 612.62158203 3.82622147 368.27001953 619.88378906 -1.23134995 358.18603516 618.54492188 2.66904068 359.33691406
		 612.88867188 -1.23134995 356.30493164 612.34521484 2.44555092 357.60961914 615.7109375 6.84017181 367.27197266
		 612.18798828 6.95761108 368.17822266 611.98242188 5.72875977 358.6940918 617.43457031 6.4185791 364.018066406
		 616.23339844 6.78253937 366.82714844 611.44628906 5.78487015 359.12719727 610.11621094 7.61264801 363.2956543
		 611.36523438 7.26664734 360.55102539 612.61816406 8.56742096 364.42138672 613.77539063 7.60041809 360.50952148
		 611.76708984 7.64881897 360.88305664 610.51464844 8.012443542 363.68969727 609.80419922 7.98381805 366.24365234
		 613.9921875 7.29164886 359.86181641 615.80566406 7.45053101 361.012207031 609.86962891 3.64397812 366.859375
		 609.36328125 3.049070358 367.22241211 611.89501953 7.32746124 360.23046875 609.0234375 2.96348 366.66650391
		 617.45410156 5.9342804 360.28027344 615.50390625 8.12860107 364.58618164 615.54541016 7.74281311 361.60864258
		 612.043457031 8.47699738 367.27514648 610.25341797 8.36099243 366.37963867 616.16845703 7.46405792 361.54785156
		 616.16796875 7.82270813 364.43286133 615.25537109 8.084739685 366.60400391 614.61279297 8.38855743 366.5925293
		 614.77539063 8.085693359 367.05859375 611.99853516 8.17490387 367.77416992 609.78027344 6.79790878 366.94580078
		 610.11767578 8.046600342 366.81225586 609.24365234 -1.23134995 366.37158203 609.59619141 -1.23134995 366.94921875;
	setAttr -s 113 ".ed[0:112]"  0 1 0 1 2 1 2 3 1 3 0 1 4 5 1 5 6 0 6 7 1
		 7 4 1 8 9 0 9 5 0 4 8 1 10 11 0 11 12 1 12 13 1 13 10 1 2 14 0 14 15 0 15 16 1 16 2 1
		 17 18 0 18 19 1 19 20 1 20 17 0 11 21 0 21 22 1 22 12 1 9 23 0 23 24 1 24 5 1 19 25 1
		 25 26 1 26 20 0 24 27 1 27 6 1 12 28 1 28 29 1 29 13 1 16 30 1 30 3 1 16 31 1 31 32 0
		 32 30 1 33 34 1 34 35 1 35 36 1 36 33 1 15 37 0 37 31 0 6 38 1 38 39 1 39 7 1 20 40 0
		 40 41 1 41 20 0 27 42 1 42 38 1 2 43 0 43 14 1 22 44 1 44 28 1 45 46 1 46 34 1 33 45 1
		 47 33 1 36 48 0 48 47 0 44 49 1 49 50 1 50 28 1 50 51 1 51 29 1 52 45 1 47 52 0 25 53 1
		 53 54 0 54 26 0 55 26 1 54 56 0 56 55 0 1 57 0 57 43 0 58 17 0 41 58 0 55 40 0 39 46 1
		 46 49 1 49 39 1 51 52 1 52 53 1 53 51 1 37 56 1 56 48 1 48 37 1 42 32 1 32 35 1 35 42 1
		 40 14 0 43 41 0 23 0 0 3 24 1 21 8 0 4 22 1 7 44 1 55 15 1 13 19 1 18 10 0 27 30 1
		 29 25 1 38 34 1 50 45 1 54 47 1 31 36 1 57 58 0;
	setAttr -s 86 ".n[0:85]" -type "float3"  1e+20 1e+20 1e+20 1e+20 1e+20
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
		 1e+20;
	setAttr -s 55 -ch 214 ".fc[0:54]" -type "polyFaces" 
		f 4 0 1 2 3
		mu 0 4 0 1 2 3
		f 4 4 5 6 7
		mu 0 4 4 5 6 7
		f 4 8 9 -5 10
		mu 0 4 8 9 5 4
		f 4 11 12 13 14
		mu 0 4 10 11 12 13
		f 4 15 16 17 18
		mu 0 4 2 14 15 16
		f 4 19 20 21 22
		mu 0 4 17 18 19 20
		f 4 23 24 25 -13
		mu 0 4 11 21 22 12
		f 4 26 27 28 -10
		mu 0 4 9 23 24 5
		f 4 -22 29 30 31
		mu 0 4 20 19 25 26
		f 4 -29 32 33 -6
		mu 0 4 5 24 27 6
		f 4 -14 34 35 36
		mu 0 4 13 12 28 29
		f 4 -3 -19 37 38
		mu 0 4 3 2 16 30
		f 4 -38 39 40 41
		mu 0 4 30 16 31 32
		f 4 42 43 44 45
		mu 0 4 33 34 35 36
		f 4 -18 46 47 -40
		mu 0 4 16 15 37 31
		f 4 -7 48 49 50
		mu 0 4 7 6 38 39
		f 3 51 52 53
		mu 0 3 20 40 41
		f 4 -34 54 55 -49
		mu 0 4 6 27 42 38
		f 3 -16 56 57
		mu 0 3 14 2 43
		f 4 -26 58 59 -35
		mu 0 4 12 22 44 28
		f 4 60 61 -43 62
		mu 0 4 45 46 34 33
		f 4 63 -46 64 65
		mu 0 4 47 33 36 48
		f 4 -60 66 67 68
		mu 0 4 28 44 49 50
		f 4 -36 -69 69 70
		mu 0 4 29 28 50 51
		f 4 71 -63 -64 72
		mu 0 4 52 45 33 47
		f 4 -31 73 74 75
		mu 0 4 26 25 53 54
		f 4 76 -76 77 78
		mu 0 4 55 26 54 56
		f 4 79 80 -57 -2
		mu 0 4 1 57 43 2
		f 4 81 -23 -54 82
		mu 0 4 58 17 20 41
		f 4 -52 -32 -77 83
		mu 0 4 40 20 26 55
		f 3 84 85 86
		mu 0 3 59 92 60
		f 3 87 88 89
		mu 0 3 61 62 93
		f 3 90 91 92
		mu 0 3 63 64 94
		f 3 93 94 95
		mu 0 3 65 95 66
		f 4 -53 96 -58 97
		mu 0 4 67 68 96 97
		f 4 -28 98 -4 99
		mu 0 4 69 70 71 98
		f 4 -25 100 -11 101
		mu 0 4 72 73 99 100
		f 4 -8 102 -59 -102
		mu 0 4 100 74 75 72
		f 4 -84 103 -17 -97
		mu 0 4 68 76 101 96
		f 4 -15 104 -21 105
		mu 0 4 77 78 102 79
		f 4 -47 -104 -79 -91
		mu 0 4 63 101 76 64
		f 4 -42 -94 -55 106
		mu 0 4 80 95 65 81
		f 4 -33 -100 -39 -107
		mu 0 4 81 69 98 80
		f 4 -30 -105 -37 107
		mu 0 4 82 102 78 83
		f 4 -62 -85 -50 108
		mu 0 4 103 92 59 84
		f 4 -72 -88 -70 109
		mu 0 4 85 62 61 86
		f 4 -66 -92 -78 110
		mu 0 4 87 94 64 88
		f 4 -45 -95 -41 111
		mu 0 4 89 66 95 90
		f 4 -44 -109 -56 -96
		mu 0 4 66 103 84 65
		f 4 -61 -110 -68 -86
		mu 0 4 92 85 86 60
		f 4 -73 -111 -75 -89
		mu 0 4 62 87 88 93
		f 4 -65 -112 -48 -93
		mu 0 4 94 89 90 63
		f 4 -67 -103 -51 -87
		mu 0 4 60 75 74 59
		f 4 -74 -108 -71 -90
		mu 0 4 93 82 83 61
		f 4 -83 -98 -81 112
		mu 0 4 91 67 97 104;
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
connectAttr "Rock_2_2Shape.iog" "aiStandardSurface1SG.dsm" -na;
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
// End of Rock_2_2.ma
