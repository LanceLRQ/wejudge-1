/**
 * General Representational State Transfer Protocol by LanceLRQ
 * Namespace: GRESTP
 * ver: 0.1
 */

(function ($) {

    $.extend({
        "GRestP": function (options) {
            var obj = Object.create(GRESTP_ENTITY);
            obj.options = options;
            obj.init();
            return obj;
        }
    });

    function isValid(options) {
        return !options || (options && typeof options === "object") ? true : false;
    }

    var GRESTP_ENTITY = {

        init: function (){
            //检测用户传进来的参数是否合法
            if (!isValid(this.options))
                throw new ReferenceError("参数对象异常");
        },

        call: function(url){
            if((typeof this.options) != 'object')
                throw new ReferenceError("参数对象异常");
            var config = $.extend({}, HTTP_OPTION_DEFAULT, this.options);
            if(typeof url == "string") config.url = url;
            $.ajax({
                url : config.url,
                type: config.method,
                data: config.data,
                cache: false,
                dataType: config.responseType,
                success: function (rel, textStatus) {
                    if(textStatus == "success"){
                        if(rel.action == "login_req"){
                            if(config.is_modal){
                                $.ModalBox({}).hide();
                                setTimeout(function () {
                                    WeJudge.login_request_dialog();
                                }, 500);
                            }else {
                                WeJudge.login_request_dialog();
                            }
                        }else {
                            if(config.responseType=='json')
                                config.callback(rel.flag, rel);
                            else
                                config.callback(true, rel);
                        }
                    }else{
                        console.log("[GRestP]请求时发生错误; 错误内容：" + textStatus);
                    }
                },
                error: function (xhr, err) {
                    console.log("[GRestP]请求时发生错误; 错误内容：" + err);
                    if(config.is_modal){
                            $.ModalBox().send_message("网络错误：" + err + "<br />请刷新界面并重试", 'danger');
                        }else{
                            $.AlertBox({
                                body: err + "<br />请刷新界面并重试",
                                color: "danger",
                                title: "网络错误"
                            }).show();
                        }
                }
            });
        },

        upload: function (url) {
            if((typeof this.options) != 'object')
                throw new ReferenceError("参数对象异常");
            if (!(window.File && window.FileReader && window.FileList && window.Blob)){
                return false;
            }
            var option = $.extend({}, UPLOAD_OPTION_DEFAULT, this.options);
            if(typeof url == "string") config.url = url;
            var xhr = new XMLHttpRequest();
            xhr.upload.addEventListener("progress", function (evt) {
                if (evt.lengthComputable) {
                    var percentComplete = Math.round(evt.loaded * 100 / evt.total);
                    option.progress(percentComplete, evt.loaded, evt.total);
                }
                else {
                    option.progress(0, 0, 0);
                }
            }, false);
            xhr.addEventListener("load", function (evt) {
                if(option.responseType == 'json'){
                    try {
                        option.success(eval("(" + evt.target.responseText + ")"));
                    }catch(ex){
                        option.error("服务器应答数据有误:" + ex);
                    }
                }else{
                    option.success(evt.target.responseText);
                }

            }, false);
            xhr.addEventListener("error", function () {
                option.error();
            }, false);
            xhr.addEventListener("abort", function () {
                option.abort();
            }, false);
            xhr.open("POST", option.url);
            xhr.send(option.formdata);
        },
        submit_form: function (forms, url) {
            this.options.data = $(forms).serialize();
            this.options.method = $(forms).attr('method');
            if(url!=undefined && url != ''){
                this.call(url);
            }else {
                this.call($(forms).attr('action'));
            }
        }
    };

    var HTTP_OPTION_DEFAULT = {
        url: '',                                //请求的url
        data: null,                             //请求的数据（QueryString）
        method: 'GET',                          //请求模式
        responseType: 'text',                   //设置jQuery的响应回调数据格式，默认为text，仅支持text和json的处理
        in_modal: false,                        //在modal框内发起的请求
        callback:function(flag, entity){}       //flag为请求是否成功的标志，然后返回请求体（或者解析好的json）
    };
    var UPLOAD_OPTION_DEFAULT = {
        url: '',                                        //请求的url
        data: null,                                     //请求的数据（QueryString）
        formdata: "",                                   //上传的表单
        responseType: 'text',                           //设置jQuery的响应回调数据格式，默认为text，仅支持text和json的处理
        success:function(data){},                       //请求成功后执行，返回响应体
        error: function (msg) {},                       //请求失败，返回消息
        abort: function () {},                          //用户终止，返回消息
        progress: function (perc, loaded, total) {}     //上传进度
    };

    // Hook
    if (!Object.create) {
        Object.create = function (o) {
            function F() {}
            F.prototype = o;
            return new F();
        };
    }
})(window.jQuery);