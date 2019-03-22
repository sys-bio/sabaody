cd "$( dirname "$0" )"
THIS_DIR=`pwd`
for port in $(seq 10100 10101)
  do python3 $THIS_DIR/migration_service.py $port &
done

wait
