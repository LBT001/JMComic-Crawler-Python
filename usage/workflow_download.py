from jmcomic import *
from jmcomic.cl import JmcomicUI

# 下方填入你要下载的本子的id，一行一个，每行的首尾可以有空白字符
jm_albums = '''
510569
390353
509898
509859
509701
494922
104105
509870
46260
24411
24182
15103
12436
11853
74560
14390
211758
509011
371875
492272
508016
507743
508536
345250
225604
507113
506489
505048
440119
216785
468031
505982
505001
504833
72726
72006
67061
67013
64150
64093
62492
57179
49009
49007
503139
502606
446711
427393
375381
181481
91320
480837
501838
502132
501916
501923
249921
198027
93008
413825
100671
497708
498873
499505
499835
494265
494738
495063
495055
396284
495342
297109
479054
484373
484874
487301
487513
487534
491216
484397
43074
136496
138356
482721
484131
420470
229401
30783
99902
138039
481536
481827
377509
480572
101327
101067
100262
358018
479915
480113




'''

# 单独下载章节
jm_photos = '''



'''


def env(name, default, trim=('[]', '""', "''")):
    import os
    value = os.getenv(name, None)
    if value is None or value == '':
        return default

    for pair in trim:
        if value.startswith(pair[0]) and value.endswith(pair[1]):
            value = value[1:-1]

    return value


def get_id_set(env_name, given):
    aid_set = set()
    for text in [
        given,
        (env(env_name, '')).replace('-', '\n'),
    ]:
        aid_set.update(str_to_set(text))

    return aid_set


def main():
    album_id_set = get_id_set('JM_ALBUM_IDS', jm_albums)
    photo_id_set = get_id_set('JM_PHOTO_IDS', jm_photos)

    helper = JmcomicUI()
    helper.album_id_list = list(album_id_set)
    helper.photo_id_list = list(photo_id_set)

    option = get_option()
    helper.run(option)
    option.call_all_plugin('after_download')


def get_option():
    # 读取 option 配置文件
    option = create_option(os.path.abspath(os.path.join(__file__, '../../assets/option/option_workflow_download.yml')))

    # 支持工作流覆盖配置文件的配置
    cover_option_config(option)

    # 把请求错误的html下载到文件，方便GitHub Actions下载查看日志
    log_before_raise()

    return option


def cover_option_config(option: JmOption):
    dir_rule = env('DIR_RULE', None)
    if dir_rule is not None:
        the_old = option.dir_rule
        the_new = DirRule(dir_rule, base_dir=the_old.base_dir)
        option.dir_rule = the_new

    impl = env('CLIENT_IMPL', None)
    if impl is not None:
        option.client.impl = impl

    suffix = env('IMAGE_SUFFIX', None)
    if suffix is not None:
        option.download.image.suffix = fix_suffix(suffix)


def log_before_raise():
    jm_download_dir = env('JM_DOWNLOAD_DIR', workspace())
    mkdir_if_not_exists(jm_download_dir)

    # 自定义异常抛出函数，在抛出前把HTML响应数据写到下载文件夹（日志留痕）
    def raises(old, msg, extra: dict):
        if ExceptionTool.EXTRA_KEY_RESP not in extra:
            return old(msg, extra)

        resp = extra[ExceptionTool.EXTRA_KEY_RESP]
        # 写文件
        from common import write_text, fix_windir_name
        write_text(f'{jm_download_dir}/{fix_windir_name(resp.url)}', resp.text)

        return old(msg, extra)

    # 应用函数
    ExceptionTool.replace_old_exception_executor(raises)


if __name__ == '__main__':
    main()
