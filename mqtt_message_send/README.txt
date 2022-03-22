1. pub.py 位於你邊緣運算裝置上，和存放人流工作紀錄檔案同一個資料夾。

linux crontab setup:
0 * * * * python3 絕對路徑/pub.py

2. sub.py 位於任一台不關機的機器上，
在接收到 pub.py的訊息之後，就會將資料輸入到你設定的 mysql。

3. 如果你想要用虛擬機作為 mqtt broker ，可以使用 AWS 或 GCP 開一台虛擬機。
作業軟體：ubuntu 18.04
防火牆規則：
	目標標記：mqtt
	來源IP範圍：0.0.0.0/0 (任何地方)
	通訊協定埠：tcp 1883

參考資料：
mqtt with python
https://ithelp.ithome.com.tw/articles/10227131