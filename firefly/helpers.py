def paginate_cursor(cursor, page_size, page_num):
    """
    returns a set of documents belonging to page number `page_num`
    where size of each page is `page_size`.

    Copy pasted from: https://www.codementor.io/arpitbhayani/fast-and-efficient-pagination-in-mongodb-9095flbqr
    """
    # Calculate number of documents to skip
    skips = page_size * (page_num - 1)

    # Skip and limit
    return cursor.skip(skips).limit(page_size)
