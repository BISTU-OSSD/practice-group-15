@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: ========================================
::   Markdown 批量补全工具
::   脚本位置：与 .bat 在同一目录
:: ========================================

:menu
cls
echo ╔══════════════════════════════════════════════════════════════╗
echo ║         Markdown Front Matter 批量补全工具                 ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo   📂 当前目录: %CD%
echo   📄 Python脚本: issue-title-fixer.py (同目录)
echo.
echo   [1] 输入文件夹路径并处理
echo   [2] 处理当前目录
echo   [3] 处理当前目录及所有子目录
echo   [4] 预览模式（不修改文件）
echo   [5] 设置 API Key
echo   [6] 查看当前配置
echo   [7] 退出
echo.
set /p choice="请选择操作 (1-7): "

if "%choice%"=="1" goto input_folder
if "%choice%"=="2" goto process_current
if "%choice%"=="3" goto process_recursive
if "%choice%"=="4" goto preview_mode
if "%choice%"=="5" goto set_key
if "%choice%"=="6" goto show_config
if "%choice%"=="7" exit /b
goto menu

:input_folder
cls
echo ╔══════════════════════════════════════════════════════════════╗
echo ║              输入文件夹路径                                 ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo   💡 提示：
echo      - 可以输入绝对路径，如：D:\my_docs\posts
echo      - 也可以输入相对路径，如：..\docs
echo      - 直接按回车使用当前目录
echo      - 可以拖拽文件夹到窗口
echo.
set /p TARGET_DIR="请输入文件夹路径: "

:: 如果用户直接回车，使用当前目录
if "%TARGET_DIR%"=="" set TARGET_DIR=.

:: 检查目录是否存在
if not exist "%TARGET_DIR%" (
    echo.
    echo ❌ 错误：目录 '%TARGET_DIR%' 不存在！
    echo.
    pause
    goto menu
)

:: 显示目录信息
echo.
echo ✅ 目标目录: %TARGET_DIR%
echo.

:: 询问是否递归处理子目录
set /p RECURSIVE="是否递归处理子目录？(Y/N，默认N): "
if /i "%RECURSIVE%"=="Y" (
    set RECURSIVE_FLAG=1
    echo 📁 将处理所有子目录
) else (
    set RECURSIVE_FLAG=0
    echo 📁 只处理当前目录
)

:: 询问是否预览
set /p PREVIEW="是否预览模式（不修改文件）？(Y/N，默认N): "
if /i "%PREVIEW%"=="Y" (
    set DRY_RUN=--dry-run
    echo 🔍 预览模式：不会修改文件
) else (
    set DRY_RUN=
    echo ✏️  正式模式：将修改文件
)

echo.
echo ========================================
echo   📋 配置确认
echo ========================================
echo   目标目录: %TARGET_DIR%
echo   Python脚本: issue-title-fixer.py (同目录)
if "%RECURSIVE_FLAG%"=="1" (echo   递归处理: 是) else (echo   递归处理: 否)
if "%DRY_RUN%"=="--dry-run" (echo   模式: 预览) else (echo   模式: 正式)
echo ========================================
echo.
set /p confirm="确认开始处理？(Y/N): "
if /i not "%confirm%"=="Y" goto menu

goto process

:process_current
cls
set TARGET_DIR=.
set RECURSIVE_FLAG=0
set DRY_RUN=
echo 📁 处理当前目录: %CD%
echo.
goto process

:process_recursive
cls
set TARGET_DIR=.
set RECURSIVE_FLAG=1
set DRY_RUN=
echo 📁 处理当前目录及所有子目录: %CD%
echo.
goto process

:preview_mode
cls
set TARGET_DIR=.
set RECURSIVE_FLAG=0
set DRY_RUN=--dry-run
echo 🔍 预览模式：处理当前目录（不会修改文件）
echo.
goto process

:set_key
cls
echo ╔══════════════════════════════════════════════════════════════╗
echo ║              设置 API Key                                   ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo   💡 当前 API Key: 
if "%DEEPSEEK_API_KEY%"=="" (
    echo      (未设置)
) else (
    echo      %DEEPSEEK_API_KEY:~0,10%...%DEEPSEEK_API_KEY:~-5%
)
echo.
echo   💡 提示：也可以直接在命令行设置环境变量
echo      set DEEPSEEK_API_KEY=sk-xxx
echo.
set /p DEEPSEEK_API_KEY="请输入新的 DeepSeek API Key (直接回车保持当前): "
if "%DEEPSEEK_API_KEY%"=="" (
    echo ⚠️  API Key 未更改
) else (
    echo ✅ API Key 已更新
)
echo.
pause
goto menu

:show_config
cls
echo ╔══════════════════════════════════════════════════════════════╗
echo ║              当前配置                                       ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo   📂 当前工作目录: %CD%
echo   📄 Python 脚本: issue-title-fixer.py
if exist "issue-title-fixer.py" (
    echo      ✅ 脚本存在
) else (
    echo      ❌ 脚本不存在！
)
echo.
echo   🔑 API Key: 
if "%DEEPSEEK_API_KEY%"=="" (
    echo      ❌ 未设置
) else (
    echo      %DEEPSEEK_API_KEY:~0,10%...%DEEPSEEK_API_KEY:~-5%
)
echo.
echo   💡 环境变量:
echo      DEEPSEEK_API_KEY=%DEEPSEEK_API_KEY%
echo.
pause
goto menu

:process
:: ========================================
::  核心处理逻辑
:: ========================================

:: 检查 Python 脚本是否在当前目录
set SCRIPT_PATH=issue-title-fixer.py
if not exist "%SCRIPT_PATH%" (
    echo ❌ 错误：找不到 issue-title-fixer.py
    echo    请确保脚本与 .bat 文件在同一目录
    echo.
    echo    当前目录: %CD%
    echo.
    pause
    goto menu
)

:: 检查 API Key
if "%DEEPSEEK_API_KEY%"=="" (
    echo ❌ 错误：未设置 API Key
    echo    请先选择 [5] 设置 API Key
    echo.
    pause
    goto menu
)

:: 创建备份目录
set BACKUP_DIR=backup_%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set BACKUP_DIR=%BACKUP_DIR: =0%
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%" 2>nul
echo 💾 备份目录: %BACKUP_DIR%
echo.

:: 统计变量
set TOTAL_FILES=0
set PROCESSED_FILES=0
set FAILED_FILES=0
set SKIPPED_FILES=0

:: 获取脚本所在目录的绝对路径
for %%i in ("%SCRIPT_PATH%") do set SCRIPT_DIR=%%~dpi
echo 📁 脚本目录: %SCRIPT_DIR%
echo.

:: 切换到目标目录
pushd "%TARGET_DIR%" 2>nul
if errorlevel 1 (
    echo ❌ 无法切换到目录: %TARGET_DIR%
    pause
    goto menu
)
set WORK_DIR=%CD%
popd

echo 📁 工作目录: %WORK_DIR%
echo.

:: 准备搜索模式
if "%RECURSIVE_FLAG%"=="1" (
    echo 🔍 递归扫描所有子目录...
    set SEARCH_OPT=/r
) else (
    echo 🔍 扫描当前目录...
    set SEARCH_OPT=
)

:: 切换到目标目录处理
pushd "%WORK_DIR%"

:: 开始遍历文件
for %SEARCH_OPT% %%f in (*.md) do (
    set /a TOTAL_FILES+=1
    
    :: 获取相对路径
    set "FILE_PATH=%%f"
    if "%RECURSIVE_FLAG%"=="1" (
        set "REL_PATH=!FILE_PATH:%WORK_DIR%\=!"
    ) else (
        set "REL_PATH=%%~nxf"
    )
    
    echo [%%TOTAL_FILES%%] 处理: !REL_PATH!
    
    :: 跳过空文件
    if %%~zf equ 0 (
        echo    ⏭️  跳过（空文件）
        set /a SKIPPED_FILES+=1
        echo.
        continue
    )
    
    :: 备份文件
    if "%RECURSIVE_FLAG%"=="1" (
        set "BACKUP_PATH=!REL_PATH:\=_!"
    ) else (
        set "BACKUP_PATH=%%~nxf"
    )
    copy "%%f" "%WORK_DIR%\..\%BACKUP_DIR%\!BACKUP_PATH!" >nul 2>&1
    
    :: 处理文件 - 使用当前目录的脚本（通过绝对路径调用）
    if "%DRY_RUN%"=="--dry-run" (
        python "%SCRIPT_DIR%issue-title-fixer.py" "%%f" --api-key %DEEPSEEK_API_KEY% --dry-run
    ) else (
        python "%SCRIPT_DIR%issue-title-fixer.py" "%%f" --api-key %DEEPSEEK_API_KEY%
    )
    
    if errorlevel 1 (
        echo    ❌ 处理失败
        set /a FAILED_FILES+=1
    ) else (
        echo    ✅ 处理成功
        set /a PROCESSED_FILES+=1
    )
    echo.
)

popd

:: 显示统计结果
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                   处理完成！                                ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo   📊 统计信息:
echo      总文件数: %TOTAL_FILES%
echo      成功处理: %PROCESSED_FILES%
echo      跳过: %SKIPPED_FILES%
echo      失败: %FAILED_FILES%
echo.
echo   💾 备份位置: %WORK_DIR%\..\%BACKUP_DIR%
echo.

:: 询问是否打开备份目录
set /p open_backup="是否打开备份目录？(Y/N): "
if /i "%open_backup%"=="Y" (
    explorer "%WORK_DIR%\..\%BACKUP_DIR%"
)

echo.
pause
goto menu