# Happy.do

# Для тестирования на локальной сети:
1. Написать мне в телеграмме (https://t.me/tema05k) с просьбой скинуть наш .env и firebasekey.json, переместить их в папку проекта
2. Скачать и активировать ngrok следуя инсрукции после регистрации (https://dashboard.ngrok.com/signup)
3. Запустить ngrok.exe и ввести команду
```
ngrok http 8080
```
4. Скопировать https адрес напротив "Forwarding" и вставить в .env в переменную "WEBHOOK_HOST" 

![image](https://github.com/Student-Labs-2023/Happy.do/assets/80484896/8af6e93e-fe76-466e-bbda-241272ad88a7)

(также в ADMIN_ID можно вставить свой telegram id для использования /admin в боте)

5. В файле bot.py раскомментировать 35 и 41 строку
   
![image](https://github.com/Student-Labs-2023/Happy.do/assets/80484896/18fd6195-a79c-4d20-b21b-23518e56d4b6)

![image](https://github.com/Student-Labs-2023/Happy.do/assets/80484896/9fc00dd8-a493-4175-b238-45799f15c3c5)



6. Запустить Docker Desktop
7. Открыть командную строку, перейти в папку с ботом
8. Собрать Docker образ командой
```
docker-compose build  
```
9. Запустить собранный образ
```  
docker-compose up
```
*Бот готов к работе* 

*Для заверешения работы бота, в консоли нажмите **Ctrl+C***
