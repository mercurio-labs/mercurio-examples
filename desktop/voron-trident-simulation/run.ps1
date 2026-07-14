$env:PYTHONIOENCODING = "utf-8"
$env:MERCURIO_WORKSPACE = $PSScriptRoot
python -X utf8 "$PSScriptRoot\sim\launch.py"
