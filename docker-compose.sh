# set -e
# cd "$(dirname "$0")"

echo `pwd`

export BAZEL_RUNID=$RANDOM
echo $BAZEL_RUNID

bazel --batch \
      --output_user_root=/root/cache/bazel \
      test --package_path=/root/tenvs \
           --spawn_strategy=standalone \
           --genrule_strategy=standalone \
           --action_env="TUSHARE_TOKEN=$TUSHARE_TOKEN" \
           --test_output=errors \
           -c opt \
           -- //...
