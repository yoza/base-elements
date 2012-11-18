class rangePagenation(object):
    """
    Return the part of page_range with length == pager_per

    """
    def __init__(self, selected_page, content_pages, pager_per=5):

        self.last_page_number = content_pages.paginator.num_pages

        if selected_page > self.last_page_number:
            selected_page = self.last_page_number
        self.page_range = content_pages.paginator.page_range

        total_cicles = self.last_page_number / pager_per
        if self.last_page_number % pager_per:
            total_cicles += 1
        k = 1
        for i in range(1, total_cicles + 1):
            m = i * pager_per + 1
            if m > self.last_page_number:
                m = self.last_page_number + 1
            if selected_page not in range(k, m):
                k += pager_per
            else:
                self.page_range = range(k, m)
                break
        super(rangePagenation, self).__init__()

    def page_range(self):
        return self.page_range
