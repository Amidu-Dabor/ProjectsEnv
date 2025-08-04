with open("high_score_file.txt", mode="r") as f:
    max_score = 0
    for num in f:
        if int(num) > max_score:
            max_score = int(num)

    print(max_score)
