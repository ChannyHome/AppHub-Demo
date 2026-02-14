-- 아이콘 만들기
https://imagemagick.org/
(명령어) ex.
magick AgentTray.png -define icon:auto-resize=256,48,32,16 AgentTray.ico

magick AgentTray.png -resize 115% -gravity center -background none -extent 512x512 AgentTray_115.png 
magick AgentTray.png -resize 118% -gravity center -background none -extent 512x512 AgentTray_final.png 
magick AgentTray.png -resize 120% -gravity center -background none -extent 512x512 AgentTray_120.png 
magick AgentTray.png -resize 125% -gravity center -background none -extent 512x512 AgentTray_125.png 
magick AgentTray.png -resize 130% -gravity center -background none -extent 512x512 AgentTray_130.png 

magick AgentTray_final.png -define icon:auto-resize=256,64,48,32,24,16 AgentTray.ico

-- Custom URL Scheme
-- 등록
powershell -ExecutionPolicy Bypass -File register_apphub.ps1
-- 조회
reg query "HKLM\SOFTWARE\Classes\apphub" /s
-- 삭제
powershell -ExecutionPolicy Bypass -File delete_apphub.ps1
-- 실행
Start-Process "apphub://open"
--실행(파라미터)
Start-Process "apphub://run?appId=Tool123"

--nginx
실행
Start-Process -FilePath "C:\nginx\nginx.exe" -WorkingDirectory "C:\nginx"

종료
Start-Process -FilePath "C:\nginx\nginx.exe" -WorkingDirectory "C:\nginx" -ArgumentList "-s","quit"

