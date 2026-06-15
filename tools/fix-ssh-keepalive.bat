@echo off
:: Fix SSH keepalive — 解决切换应用后断开的问题
:: 以管理员身份运行此脚本

set CFG=C:\ProgramData\ssh\sshd_config

echo === 当前 keepalive 配置 ===
findstr /i "ClientAlive TCPKeepAlive" %CFG%

echo.
echo === 修改配置 ===
powershell -Command "(Get-Content '%CFG%' -Raw) -replace '#ClientAliveInterval 0', 'ClientAliveInterval 30' -replace '#ClientAliveCountMax 3', 'ClientAliveCountMax 3' | Set-Content '%CFG%' -NoNewline"

echo === 修改后 ===
findstr /i "ClientAlive TCPKeepAlive" %CFG%

echo.
echo === 重启 sshd ===
net stop sshd
net start sshd

echo.
echo === 完成 ===
echo ClientAliveInterval=30s, 最多丢3次心跳(90s)后断开
pause
