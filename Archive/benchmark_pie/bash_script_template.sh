for file in ./test_cases/input*.txt; do
    echo "Processing $file"
    ./${EXE_NAME} < "$file"
done