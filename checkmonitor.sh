#!/bin/bash  

proc_name="python"       
proc_path=`pwd`
proc_num()                     
{
    num=`ps -ef | grep $proc_name | grep -v grep | wc -l`
    return $num
}
                
while sleep 30
do
    proc_num  
    number=$?      
    if [ $number -eq 0 ]           
    then                           
    cd `dirname $0`; ./start.sh -c 1
    fi
done