#!/usr/bin/bash



tmp_dir=$(mktemp -d)

safe_exit(){
	rm -rfv "$tmp_dir"
}

# trap safe_exit EXIT


if [ -z "$1" ];then
	echo "使用： $0 <插件目录名>"
	exit 1
fi


if [ -d "$1" ];then
	plugin_name="$1"
else
	echo "需要插件目录"
	exit 1
fi

(
cd "$plugin_name"
cp -av . "$tmp_dir"
)

FUNCS_PY="$tmp_dir/$plugin_name/funcs.py"

if [ -L "$FUNCS_PY" ];then
	rm -v "$FUNCS_PY"
	cp -v funcs.py "$FUNCS_PY"
fi

(
cd "$tmp_dir"
python3 -m zipfile -c ../"${plugin_name}.pyz" .
)

pwd -P

if [ $? -eq 0 ];then
	echo "插件打包成功"
	mv -v "${tmp_dir}/../${plugin_name}.pyz" .
else
	echo "插件打包失败"
fi