ps -ef | grep python | grep -v grep | awk  '{print $2}' | xargs kill
echo "" > monitor.log
nohup python ./monitor.py 1>monitor.log  2>&1 &
