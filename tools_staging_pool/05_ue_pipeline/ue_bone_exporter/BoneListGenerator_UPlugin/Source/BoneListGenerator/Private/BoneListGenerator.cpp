#include "BoneListGenerator.h"
#include "ContentBrowserModule.h"
#include "IContentBrowserSingleton.h"
#include "ToolMenus.h"
#include "Engine/SkeletalMesh.h"
#include "Animation/Skeleton.h"
#include "Misc/FileHelper.h"
#include "DesktopPlatformModule.h"
#include "Framework/Application/SlateApplication.h"
#include "HAL/PlatformFileManager.h"

#define LOCTEXT_NAMESPACE "FBoneListGeneratorModule"

void FBoneListGeneratorModule::StartupModule()
{
	// 等待 ToolMenus 初始化完成后注册菜单
	UToolMenus::RegisterStartupCallback(FSimpleMulticastDelegate::FDelegate::CreateRaw(this, &FBoneListGeneratorModule::RegisterMenuExtensions));
}

void FBoneListGeneratorModule::ShutdownModule()
{
	UnregisterMenuExtensions();
}

void FBoneListGeneratorModule::RegisterMenuExtensions()
{
	// 获取 SkeletalMesh 资产的右键菜单
	UToolMenu* Menu = UToolMenus::Get()->ExtendMenu("ContentBrowser.AssetContextMenu.SkeletalMesh");
	
	if (Menu)
	{
		FToolMenuSection& Section = Menu->FindOrAddSection("GetAssetActions");
		
		Section.AddMenuEntry(
			"ExportBoneList",
			LOCTEXT("ExportBoneList", "生成骨骼表"),
			LOCTEXT("ExportBoneListTooltip", "将选中骨骼网格体的所有骨骼名称导出到txt文件"),
			FSlateIcon(),
			FToolMenuExecuteAction::CreateLambda([](const FToolMenuContext& Context)
			{
				// 获取选中的资产
				UContentBrowserAssetContextMenuContext* AssetContext = Context.FindContext<UContentBrowserAssetContextMenuContext>();
				if (!AssetContext)
				{
					return;
				}

				// 遍历选中的骨骼网格体
				for (const FAssetData& AssetData : AssetContext->SelectedAssets)
				{
					USkeletalMesh* SkeletalMesh = Cast<USkeletalMesh>(AssetData.GetAsset());
					if (!SkeletalMesh)
					{
						continue;
					}

					// 获取骨架
					USkeleton* Skeleton = SkeletalMesh->GetSkeleton();
					if (!Skeleton)
					{
						UE_LOG(LogTemp, Warning, TEXT("骨骼网格体 %s 没有关联的骨架"), *SkeletalMesh->GetName());
						continue;
					}

					// 获取引用骨架
					const FReferenceSkeleton& RefSkeleton = Skeleton->GetReferenceSkeleton();
					int32 BoneCount = RefSkeleton.GetNum();

					// 构建骨骼名称列表
					FString BoneListContent;
					for (int32 i = 0; i < BoneCount; i++)
					{
						FName BoneName = RefSkeleton.GetBoneName(i);
						BoneListContent += BoneName.ToString() + TEXT("\n");
					}

					// 打开保存文件对话框
					IDesktopPlatform* DesktopPlatform = FDesktopPlatformModule::Get();
					if (DesktopPlatform)
					{
						TArray<FString> OutFiles;
						FString DefaultPath = FPaths::ProjectDir();
						FString DefaultFileName = SkeletalMesh->GetName() + TEXT("_BoneList.txt");

						bool bSaved = DesktopPlatform->SaveFileDialog(
							FSlateApplication::Get().FindBestParentWindowHandleForDialogs(nullptr),
							TEXT("保存骨骼表"),
							DefaultPath,
							DefaultFileName,
							TEXT("文本文件 (*.txt)|*.txt"),
							0,
							OutFiles
						);

						if (bSaved && OutFiles.Num() > 0)
						{
							// 保存文件
							if (FFileHelper::SaveStringToFile(BoneListContent, *OutFiles[0], FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM))
							{
								UE_LOG(LogTemp, Log, TEXT("骨骼表已保存到: %s"), *OutFiles[0]);
								
								// 显示成功消息
								FText Message = FText::Format(
									LOCTEXT("ExportSuccess", "成功导出 {0} 个骨骼到:\n{1}"),
									FText::AsNumber(BoneCount),
									FText::FromString(OutFiles[0])
								);
								FMessageDialog::Open(EAppMsgType::Ok, Message);
							}
							else
							{
								UE_LOG(LogTemp, Error, TEXT("保存骨骼表失败: %s"), *OutFiles[0]);
							}
						}
					}
				}
			})
		);
	}
}

void FBoneListGeneratorModule::UnregisterMenuExtensions()
{
	UToolMenus::UnRegisterStartupCallback(this);
	UToolMenus::UnregisterOwner(this);
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FBoneListGeneratorModule, BoneListGenerator)
