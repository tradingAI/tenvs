set -e
cd "$(dirname "$0")"

echo `pwd`

chmod -R 777 /root/cache/bazel
chmod -R 777 /root/output

export BAZEL_RUNID=$RANDOM

bazel --batch \
      --output_user_root=/root/cache/bazel \
      test --package_path=/root/tenvs \
           --spawn_strategy=standalone \
           --genrule_strategy=standalone \
           --action_env="TUSHARE_TOKEN=$TUSHARE_TOKEN" \
           --test_output=errors \
           -c opt \
           -- //...
