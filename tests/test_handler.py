import handler


def test_to_csv():
    out = handler.to_csv(["a", "b"], [[1, 2]]).decode()
    assert out.splitlines() == ["a,b", "1,2"]


def test_channel_rows():
    ch = {"id": "C1", "snippet": {"title": "T"},
          "statistics": {"subscriberCount": "5", "viewCount": "9", "videoCount": "2"}}
    assert handler.channel_rows(ch, "ts") == [["ts", "C1", "T", "5", "9", "2"]]


def test_video_rows_missing_likes():
    v = {"id": "V1", "snippet": {"title": "x", "publishedAt": "p"},
         "contentDetails": {"duration": "PT1M"}, "statistics": {"viewCount": "3"}}
    assert handler.video_rows([v], "ts")[0][-2:] == [None, None]
