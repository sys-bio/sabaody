cd "$( dirname "${BASH_SOURCE[0]}" )"
THIS_DIR=`pwd`
for port in $(seq 10100 10400)
  do $THIS_DIR/migration_service.py $port &
done

wait
