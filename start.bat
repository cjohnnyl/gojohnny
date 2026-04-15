@echo off
setlocal enabledelayedexpansion

echo.
echo  GoJohnny — Setup e inicializacao
echo  ==================================
echo.

:: -------------------------------------------------------
:: 1. Verificar se o .venv existe
:: -------------------------------------------------------
if not exist ".venv\Scripts\activate.bat" (
    echo [AVISO] Virtualenv nao encontrado. Criando .venv...
    python -m venv .venv
    if errorlevel 1 (
        echo [ERRO] Falha ao criar o virtualenv. Verifique se o Python 3.11+ esta instalado.
        exit /b 1
    )
    echo [OK] Virtualenv criado.
) else (
    echo [OK] Virtualenv encontrado.
)

:: -------------------------------------------------------
:: 2. Ativar o virtualenv
:: -------------------------------------------------------
call .venv\Scripts\activate.bat
echo [OK] Virtualenv ativado.

:: -------------------------------------------------------
:: 3. Instalar dependencias
:: -------------------------------------------------------
echo.
echo Instalando dependencias...
pip install -r backend/requirements.txt --quiet
if errorlevel 1 (
    echo [ERRO] Falha ao instalar dependencias.
    exit /b 1
)
echo [OK] Dependencias instaladas.

:: -------------------------------------------------------
:: 4. Verificar se o .env existe
:: -------------------------------------------------------
if not exist ".env" (
    echo.
    echo [AVISO] Arquivo .env nao encontrado na raiz do projeto.
    echo         Copiando .env.example para .env...
    copy ".env.example" ".env" >nul
    echo [ATENCAO] Abra o arquivo .env e preencha OPENAI_API_KEY e JWT_SECRET_KEY antes de continuar.
    pause
    exit /b 1
)
echo [OK] Arquivo .env encontrado.

:: -------------------------------------------------------
:: 5. Verificar se OPENAI_API_KEY esta preenchida
:: -------------------------------------------------------
set "API_KEY_OK=0"
for /f "usebackq tokens=1,* delims==" %%A in (".env") do (
    if "%%A"=="OPENAI_API_KEY" (
        if not "%%B"=="" set "API_KEY_OK=1"
    )
)

if "!API_KEY_OK!"=="0" (
    echo.
    echo [ATENCAO] OPENAI_API_KEY nao esta configurada no arquivo .env
    echo           O chatbot nao vai funcionar sem ela.
    echo           Abra o .env e preencha: OPENAI_API_KEY=sk-...
    echo.
    echo Pressione qualquer tecla para subir o servidor mesmo assim (para testar outras rotas)
    echo ou feche esta janela para cancelar.
    pause
)

:: -------------------------------------------------------
:: 6. Subir o servidor
:: -------------------------------------------------------
echo.
echo Subindo o servidor GoJohnny...
echo Acesse: http://localhost:8000/docs
echo Pressione Ctrl+C para encerrar.
echo.

cd backend
uvicorn app.main:app --reload --port 8000

endlocal
