# Test the logic of how tags are picked

podio_tags = 'v00-16 v00-16-01 v00-16-02 v00-16-03 v00-16-04 v00-16-05'.split()
edm4hep_tags = 'v00-07 v00-07-01 v00-07-02 v00-08 v00-09'.split()
podio_dates = ['2022-10-06 14:05:30 +0200',
               '2022-12-14 11:56:11 +0100',
               '2022-12-19 13:50:19 +0100',
               '2023-03-14 16:53:43 +0100',
               '2023-05-23 14:51:09 +0200',
               '2023-05-23 18:25:45 +0200']
edm4hep_dates = ['2022-10-06 14:07:18 +0200',
                 '2022-10-18 18:01:42 +0200',
                 '2022-12-14 14:09:47 +0100',
                 '2023-04-18 16:44:53 +0200',
                 '2023-06-06 16:38:12 +0200']


i = 0
j = 0
while i < len(podio_tags) and j < len(edm4hep_tags):
    # print(f'{podio_tags[i]} {edm4hep_tags[j]}')
    print(f'{podio_tags[i]} {edm4hep_tags[j]}')

    if i == len(podio_tags) - 1:
        j += 1
        continue
    if j == len(edm4hep_tags) - 1:
        i += 1
        continue
    # If there is a newer version of edm4hep
    # but this is still older than the next podio version
    # then increase the edm4hep version
    if edm4hep_dates[j+1] < podio_dates[i+1]:
        j += 1
        continue

    if edm4hep_dates[j+1] > podio_dates[i+1]:
        i += 1
        continue
