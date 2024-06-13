#!/bin/sh

echo "Content-Type: application/json"
echo ""

token="token_id"
signalfile="/www/pppwn/stop"
attempts=0

read postData

token=$(echo $postData | sed -n 's/^.*token=\([^&]*\).*$/\1/p' | sed "s/%20/ /g")
adapter=$(echo $postData | sed -n 's/^.*adapter=\([^&]*\).*$/\1/p' | sed "s/%20/ /g")
version=$(echo $postData | sed -n 's/^.*version=\([^&]*\).*$/\1/p' | sed "s/%20/ /g")
stage1=$(echo $postData | sed -n 's/^.*stage1=\([^&]*\).*$/\1/p' | sed "s/%20/ /g")
stage1=$(echo "$stage1" | sed 's/%2F/\//g')
stage2=$(echo $postData | sed -n 's/^.*stage2=\([^&]*\).*$/\1/p' | sed "s/%20/ /g")
stage2=$(echo "$stage2" | sed 's/%2F/\//g')
timeout$(echo $postData | sed -n 's/^.*timeout=\([^&]*\).*$/\1/p' | sed "s/%20/ /g")
task=$(echo $postData | sed -n 's/^.*task=\([^&]*\).*$/\1/p' | sed "s/%20/ /g")
option=$(echo $postData | sed -n 's/^.*option=\([^&]*\).*$/\1/p' | sed "s/%20/ /g")
root=$(echo $postData | sed -n 's/^.*root=\([^&]*\).*$/\1/p' | sed "s/%20/ /g")
root=$(echo "$root" | sed 's/%2F/\//g')

if [ -z "$timeout" ]; then
    timeout=0
fi
if [ -z "$root" ]; then
    root="/root"
fi

if [ "$token" = "token_id" ]; then

    case "$task" in
    "setup")

        source=""
        if [ "$option" = "aarch64-linux-musl" ]; then
            source="https://nightly.link/xfangfang/PPPwn_cpp/workflows/ci.yaml/main/aarch64-linux-musl.zip"
        elif [ "$option" = "arm-linux-musleabi(cortex_a7)" ]; then
            source="https://nightly.link/xfangfang/PPPwn_cpp/workflows/ci.yaml/main/arm-linux-musleabi%28cortex_a7%29.zip"
        elif [ "$option" = "arm-linux-musleabi(pi_zero_w)" ]; then
            source="https://nightly.link/xfangfang/PPPwn_cpp/workflows/ci.yaml/main/arm-linux-musleabi%28pi_zero_w%29.zip"
        elif [ "$option" = "arm-linux-musleabi(mpcorenovfp)" ]; then
            source="https://nightly.link/xfangfang/PPPwn_cpp/workflows/ci.yaml/main/arm-linux-musleabi%28mpcorenovfp%29.zip"
        elif [ "$option" = "x86_64-linux-musl" ]; then
            source="https://nightly.link/xfangfang/PPPwn_cpp/workflows/ci.yaml/main/x86_64-linux-musl.zip"
        elif [ "$option" = "mipsel-linux-musl" ]; then
            source="https://nightly.link/xfangfang/PPPwn_cpp/workflows/ci.yaml/main/mipsel-linux-musl.zip"
        elif [ "$option" = "mips-linux-musl" ]; then
            source="https://nightly.link/xfangfang/PPPwn_cpp/workflows/ci.yaml/main/mips-linux-musl.zip"
        fi

        if ! command -v "unzip" > /dev/null 2>&1; then
            "$(opkg update)"
            "$(opkg install unzip)"
        fi

        cd /tmp/
        if wget -O pppwn_file.zip $source; then
            "$(unzip pppwn_file.zip)"
            "$(rm pppwn_file.zip)"
            "$(tar -xzvf pppwn.tar.gz)"
            "$(rm pppwn.tar.gz)"
            "$(chmod +x pppwn)"
            "$(mv pppwn /usr/bin)"
            echo "{\"output\":\"PPPwn installed!\",\"pppwn\":true}"
            exit 0
        else
            echo "{\"output\":\"Cannot to get source: $source\"}"
            exit 1
        fi

    ;;
    "state")

        echo "{"
        if command -v pppoe-server >/dev/null 2>&1; then
            rspppoe=$(/etc/init.d/pppoe-server status)
            echo "\"pppoe\":\"$rspppoe\",";
        fi
        if command -v pppwn > /dev/null 2>&1; then
            echo "\"pppwn\":true,"
            echo "\"interfaces\":["
            parts=$(pppwn list | sed "s/\s*$/\"},/")
            if [ "$parts" != "" ]; then
                eths=$(echo "$parts" | sed "s/^\s*/{\"adapter\":\"/")
                echo $eths | sed "s/,$//"
            fi
            echo "],";
            if pgrep pppwn > /dev/null; then
                echo "\"running\":true,"
            else
                echo "\"running\":false,"
                if [ -f "$signalfile" ]; then
                    rm $signalfile
                fi
            fi
            payloads=$(ls /root/offsets/*.bin)
            filename=""
            separator=""
            echo "\"versions\":["
            for payload in $payloads; do

                if echo "$payload" | grep -q "stage1"; then
                    filename=$(echo $payload | sed -e 's/.*_//g' -e 's/\.bin//g')
                    echo "$separator\"$filename\""
                fi
                if [ "$separator" = "" ]; then
                    separator=","
                fi

            done
            separator=""
            echo "],\"offsets\":{"
            for payload in $payloads; do

                filename=$(echo $payload | sed -e 's/.*_//g' -e 's/\.bin//g')
                if echo "$payload" | grep -q "stage1"; then
                    echo "$separator\"stage1-$filename\":\"$payload\""
                elif echo "$payload" | grep -q "stage2"; then
                    echo "$separator\"stage2-$filename\":\"$payload\""
                fi
                if [ "$separator" = "" ]; then
                    separator=","
                fi

            done
            echo "},"
            if [ -f /root/pw.conf ];then
                source /root/pw.conf
                echo "\"adapter\":\"$inputAdapter\","
                echo "\"timeout\":\"$inputTimeout\","
                echo "\"version\":\"$inputVersion\","
            fi
        else
            echo "\"pppwn\":false,"
            echo "\"compiles\":["
            type=$(uname -m)
            if echo "$type" | grep -q "arch64"; then
                echo "{\"label\":\"Arch64 Linux\",\"type\":\"aarch64-linux-musl\"}"
            elif echo "$type" | grep -q "arm"; then
                echo "{\"label\":\"Arm Cortex A7\",\"type\":\"arm-linux-musleabi(cortex_a7)\"},"
                echo "{\"label\":\"Arm Pi Zero W\",\"type\":\"arm-linux-musleabi(pi_zero_w)\"},"
                echo "{\"label\":\"Arm MP Core Nov Fp\",\"type\":\"arm-linux-musleabi(mpcorenovfp)\"}"
            elif echo "$type" | grep -q "x86_64"; then
                echo "{\"label\":\"X86-64 Linux\",\"type\":\"x86_64-linux-musl\"}"
            elif echo "$type" | grep -q "mips"; then
                echo "{\"label\":\"MIPSEL Linux\",\"type\":\"mipsel-linux-musl\"},"
                echo "{\"label\":\"MIPS Linux\",\"type\":\"mips-linux-musl\"}"
            elif "$type" | grep -q "mipsel"; then
                echo "{\"label\":\"MIPSEL Linux\",\"type\":\"mipsel-linux-musl\"}"
            fi
            echo "],"
        fi
        if grep -q "/root/run.sh" /etc/rc.local; then
            echo "\"autorun\":true"
        else
            echo "\"autorun\":false"
        fi
        echo "}"

    ;;
    "start")

        if /etc/init.d/pppoe-server status | grep -q "running"; then
            /etc/init.d/pppoe-server stop
            sleep 3
        fi

        ip link set $adapter down
        sleep 5
        ip link set $adapter up

        echo -e "inputAdapter=$adapter\n" > /root/pw.conf
        echo -e "inputTimeout=$timeout" >> /root/pw.conf
        echo -e "inputVersion=$version" >> /root/pw.conf

        attempts=$((attempts+1))

        result=$(pppwn --interface "$adapter" --fw "$version" --stage1 "$stage1" --stage2 "$stage2" --timeout $timeout --auto-retry)
        
        if [[ "$result" == *"\[\+\] Done\!"* ]]; then
            /etc/init.d/pppoe-server start
            echo "{\"output\":\"Exploit success!\",\"pppwned\":true,\"attempts\":\"$attempts\"}"
            exit 0
        else
            echo "{\"output\":\"Exploit interrupted!\",\"pppwned\":false,\"attempts\":\"$attempts\"}"
            exit 1
        fi

    ;;
    "stop")

        pids=$(pgrep pppwn)
        for pid in $pids; do
            kill $pid
        done

        echo "{\"output\":\"Execution terminated.\",\"pppwned\":false,\"attempts\":\"$attempts\"}"

        exit 1

    ;;
    "enable")

        if ! grep -q "/root/run.sh" /etc/rc.local; then
            sed -i '/exit 0/d' /etc/rc.local
            echo "/root/run.sh &" >> /etc/rc.local
            echo "exit 0" >> /etc/rc.local
        fi
        
        if grep -q "interface=" "/root/run.sh"; then
            sed -i "s/interface=\".*\"/interface=\"$adapter\"/" "/root/run.sh"
        fi
        if grep -q "version=" "/root/run.sh"; then
            sed -i "s/version=\".*\"/version=\"$version\"/" "/root/run.sh"
        fi

        if [ -f "$signalfile" ]; then
            rm $signalfile
        fi

        chmod +x /etc/rc.local
        chmod +x /root/run.sh
        echo "{\"output\":\"Autorun enable\"}"

    ;;
    "disable")

        if grep -q "/root/run.sh" /etc/rc.local; then
            sed -i '/\/root\/run\.sh/d' /etc/rc.local
        fi

        echo "{\"output\":\"Autorun disabled\"}"

    ;;
    "update")

        "$(cd /root/)"
        if [ -d ~/offsets ]; then
            "$(rm -r ~/offsets)"
        fi
        if [ -d /www/pppwn ]; then
            "$(rm -r /www/pppwn)"
        fi
        if [ -f /www/pppwn.html ]; then
            "$(rm /www/pppwn.html)"
        fi
        if [ -f /www/cgi-bin/pw.cgi ]; then
            "$(rm /www/cgi-bin/pw.cgi)"
        fi
        if [ -f ~/run.sh ]; then
            "$(rm ~/run.sh)"
        fi
        if command -v pppwn > /dev/null 2>&1; then
            "$(rm /usr/bin/pppwn)"
        fi
        if ! command -v unzip > /dev/null 2>&1; then
            "$(opkg update)"
            "$(opkg install unzip)"
        fi

        "$(cd /tmp/)"
        
        "$(wget -O main.zip https://github.com/CodeInvers3/PPPwn_ow/archive/refs/heads/main.zip)"
        "$(unzip main.zip)"
        
        cd PPPwn_ow-main
        
        "$(mv -f offsets /root/)"
        "$(mv -f www/pppwn /www)"
        "$(mv -f www/pppwn.html /www)"
        "$(mv -f www/cgi-bin/pw.cgi /www/cgi-bin)"
        "$(mv -f run.sh /root/)"
        
        cd ..
        
        "$(rm -r PPPwn_ow-main main.zip)"
        "$(chmod +x /www/cgi-bin/pw.cgi)"
        echo "{\"output\":\"Update completed!\"}"
        exit 0
        
    ;;
    "connect")

        echo "{"
        if /etc/init.d/pppoe-server status | grep -q "running"; then
            /etc/init.d/pppoe-server stop
            echo "\"output\":\"Stop pppoe service\","
        elif /etc/init.d/pppoe-server status | grep -q "inactive"; then
            /etc/init.d/pppoe-server start
            echo "\"output\":\"Start pppoe service\","
        fi
        rspppoe=$(/etc/init.d/pppoe-server status)
        echo "\"pppoe\":\"$rspppoe\""
        echo "}"

    ;;
    *)
        echo "{\"output\":\"null\"}"
        exit 1
    ;;
    esac

else
    echo "{\"output\":\"Invalid token!\"}"
    exit 1
fi