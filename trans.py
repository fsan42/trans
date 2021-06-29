import json
import re
import demjson
import execjs
import requests
import pyperclip
import sys


def get_common(session, headers):
    response = session.get("http://fanyi.baidu.com", )
    cookie = requests.utils.dict_from_cookiejar(response.cookies)["BAIDUID"]

    html = session.get("http://fanyi.baidu.com", headers=headers).text
    common = re.findall("window\[\'common\'\] = ([\s\S]*)(// 图片翻译小流量)", html)[0][0] + "}"

    return demjson.decode(common)


def get_sign(query):
    code = r'''function e(r) {
    const o = r.match(/[\uD800-\uDBFF][\uDC00-\uDFFF]/g);
    if (null === o) {
        const t = r.length;
        t > 30 && (r = "" + r.substr(0, 10) + r.substr(Math.floor(t / 2) - 5, 10) + r.substr(-10, 10))
    } else {
        let f = [];
        let h = e.length;
        let e = r.split(/[\uD800-\uDBFF][\uDC00-\uDFFF]/);
        let C = 0;
        for (; h > C; C++)
            "" !== e[C] && f.push.apply(f, a(e[C].split(""))),
            C !== h - 1 && f.push(o[C]);
        const g = f.length;
        g > 30 && (r = f.slice(0, 10).join("") + f.slice(Math.floor(g / 2) - 5, Math.floor(g / 2) + 5).join("") + f.slice(-10).join(""))
    }
    for (var m = 320305 , s = 131321201, S = [], c = 0, v = 0; v < r.length; v++) {
        var A = r.charCodeAt(v);
        128 > A ? S[c++] = A : (2048 > A ? S[c++] = A >> 6 | 192 : (55296 === (64512 & A) && v + 1 < r.length && 56320 === (64512 & r.charCodeAt(v + 1)) ? (A = 65536 + ((1023 & A) << 10) + (1023 & r.charCodeAt(++v)),
            S[c++] = A >> 18 | 240,
            S[c++] = A >> 12 & 63 | 128) : S[c++] = A >> 12 | 224,
            S[c++] = A >> 6 & 63 | 128),
            S[c++] = 63 & A | 128)
    }
    for (var p = m, F = "" + String.fromCharCode(43) + String.fromCharCode(45) + String.fromCharCode(97) + ("" + String.fromCharCode(94) + String.fromCharCode(43) + String.fromCharCode(54)), D = "" + String.fromCharCode(43) + String.fromCharCode(45) + String.fromCharCode(51) + ("" + String.fromCharCode(94) + String.fromCharCode(43) + String.fromCharCode(98)) + ("" + String.fromCharCode(43) + String.fromCharCode(45) + String.fromCharCode(102)), b = 0; b < S.length; b++)
        p += S[b], p = n(p, F);
    return p = n(p, D),
        p ^= s,
    0 > p && (p = (2147483647 & p) + 2147483648),
        p %= 1e6,
    p.toString() + "." + (p ^ m)
}
function n(r, o) {
    for (let t = 0; t < o.length - 2; t += 3) {
        let a = o.charAt(t + 2);
        a = a >= "a" ? a.charCodeAt(0) - 87 : Number(a),
            a = "+" === o.charAt(t + 1) ? r >>> a : r << a,
            r = "+" === o.charAt(t) ? r + a & 4294967295 : r ^ a
    }
    return r
}
'''
    # code = code.de("utf-8").decode("utf-8")

    # with open("sign.js", encoding="utf-8", mode="r") as f:
    #     code = f.read()

    ctx = execjs.compile(code)
    return ctx.call("e", query)


def get_lan_to(session, query, headers):
    data = {
        'query': query
    }

    response = session.post('https://fanyi.baidu.com/langdetect', headers=headers, data=data)
    lan = json.loads(response.text)["lan"]

    to = "en" if lan == "zh" else "zh"
    return lan, to


def get_res_and_set(lan, to, query, sign, session, common, headers):
    data = {
        'from': lan,
        'to': to,
        'query': query,
        'transtype': 'realtime',
        'simple_means_flag': '3',
        'sign': sign,
        'token': common["token"],
        'domain': 'common'
    }

    response = session.post('https://fanyi.baidu.com/v2transapi', headers=headers, data=data)
    response = json.loads(response.text)
    res = response['trans_result']['data'][0]['dst']
    print(res)
    pyperclip.copy(res)


if __name__ == '__main__':
    headers = {
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'Origin': 'https://fanyi.baidu.com',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Accept': '*/*',
        'X-Requested-With': 'XMLHttpRequest',
        'Connection': 'keep-alive',
    }
    session = requests.session()

    common = get_common(session, headers)

    query = " ".join(sys.argv[1:])
    print(query)

    sign = get_sign(query)
    lan, to = get_lan_to(session, query, headers)
    get_res_and_set(lan, to, query, sign, session, common, headers)
