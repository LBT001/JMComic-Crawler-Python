from jmcomic import *
from jmcomic.cl import JmcomicUI

# 下方填入你要下载的本子的id，一行一个，每行的首尾可以有空白字符
jm_albums = '''
478550
479549
450021
477708
477547
77761
94788
185891
226878
476148
239642
474823
474824
475023
472275
472250
472952
469957
346609
469956
471693
148632
241928
465604
467116
459066
460836
462097
463565
5440
306848
250733
333722
131674
82938
187089
424037
247293
238928
237158
294455
141989
224879
54481
85798
121295
214180
333696
102464
45589
401327
212911
410841
224412
151164
221425
293750
346821
279371
283485
92594
291175
213232
74359
60792
55525
459036
457423
274792
98154
90520
90544
37308
182135
90521
178760
75365
456213
455959
151855
455595
455642
455062
454803
364652
449673
449672
451603
208592
251258
448136
448135
448134
438501
449581
92063
448061
268189
447891
2653





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
