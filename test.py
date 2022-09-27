with open('books.txt') as file:
    contents = file.read()
    search_word = input("enter a word you want to search in file: ")
    if search_word in contents:
        print ('word found')
    else:
        print ('word not found')

