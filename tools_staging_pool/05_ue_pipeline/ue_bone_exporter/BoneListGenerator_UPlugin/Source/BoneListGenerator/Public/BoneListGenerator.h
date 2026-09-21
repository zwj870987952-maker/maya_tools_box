#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FBoneListGeneratorModule : public IModuleInterface
{
public:
	/** IModuleInterface implementation */
	virtual void StartupModule() override;
	virtual void ShutdownModule() override;

private:
	/** 注册右键菜单 */
	void RegisterMenuExtensions();
	
	/** 取消注册右键菜单 */
	void UnregisterMenuExtensions();
};
