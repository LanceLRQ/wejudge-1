
(function ($) {

    $.extend({
        "ModalBox": function (options) {
            var obj = Object.create(ModalBox);
            obj.options = options;
            obj.init();
            return obj;
        },
        "AlertBox":  function (options) {
            var obj = Object.create(AlertBox);
            obj.options = options;
            obj.init();
            return obj;
        },
        "ConfirmBox":  function (options) {
            var obj = Object.create(ConfirmBox);
            obj.options = options;
            obj.init();
            return obj;
        }
    });

    function isValid(options) {
        return !options || (options && typeof options === "object") ? true : false;
    }

        // Bootstrap 模态框控制封装包
    var ModalBox = {
        init: function(){
            //检测用户传进来的参数是否合法
            if (!isValid(this.options))
                this.options = undefined;
        },
        hide: function () {
            $("#generalModal").modal('hide');
        },
        reshow: function (){
            $("#generalModal").modal('show');
        },
        send_message: function (msg, color) {
            if(color == undefined || color == ''){
                color = 'danger';
            }
            $("#modal-body-messager").html(msg).removeClass().addClass("alert alert-" + color).show();
        },
        clean_message: function () {
            $("#modal-body-messager").hide();
        },
        show: function () {
            this.build();
        },
        ClickDefBtn: function () {
            this.option.default_btn_action();
        },
        build:function(){
            if(this.options == undefined){
                console.log("非法请求");
                return false;
            }
            var option = $.extend({}, Modal_Option_Default, this.options);
            var $generalModal = $("#generalModal");
            var $generalModalDoc = $("#generalModalDoc");
            var $modal_body = $("#modal-body");
            var $modal_title = $("#modal-title");
            var $modal_default_action_btn = $("#modal-default-action-btn");
            var $modal_close_action_btn = $("#modal-close-action-btn");

            switch (option.size){
                case 'large':
                    $generalModalDoc.removeClass().addClass('modal-dialog modal-lg');
                    break;
                case 'small':
                    $generalModalDoc.removeClass().addClass('modal-dialog modal-sm');
                    break;
                default:
                    $generalModalDoc.removeClass().addClass('modal-dialog');
                    break;
            }

            $modal_body.html("<div align='center'>载入中...</div>");
            $modal_title.text(option.title);
            $modal_default_action_btn.text(option.default_btn_title).removeClass().addClass('btn btn-' + option.default_btn_color);
            $modal_default_action_btn.click(Modal_Option_Default.default_btn_action);
            $generalModal.modal('show');
            if(option.close_btn_visiable){
                $modal_close_action_btn.show()
            }else{
                $modal_close_action_btn.hide();
            }
            if(option.mode=='url'){
                var urlhash = option.url;
                if(urlhash.indexOf('?') > -1){
                    urlhash = urlhash  + "&rand=" + Math.random();
                }
                else{
                    urlhash = urlhash  + "?rand=" + Math.random();
                }
                $.GRestP({
                    method: "GET",
                    responseType: "text",
                    callback: function (flag, data) {
                        if(flag){
                            $modal_default_action_btn.unbind('click');
                            $modal_default_action_btn.click(option.default_btn_action);
                            $modal_body.html(data);
                            option.loaded(); //加载完成后执行回调
                        }else{
                            $modal_body.text("加载失败！");
                            $modal_default_action_btn.text("确定").click(function () {
                                $generalModal.modal('hide');
                            });
                        }
                    }
                }).call(urlhash);

            }else{
                $modal_default_action_btn.unbind('click');
                $modal_default_action_btn.click(option.default_btn_action);
                $modal_body.html(option.html);
                option.loaded(); //加载完成后执行回调
            }
        }
    };

    var AlertBox = {
        init: function() {
            if (!isValid(this.options))
                throw new ReferenceError("参数对象异常");
        },
        show: function () {
            var option = $.extend({}, Alertbox_Option_Default, this.options);
            $("#alertbox-yes-btn")
                .removeClass()
                .addClass('btn btn-' + option.color)
                .unbind('click')
                .click(function () {
                    $("#alertbox").modal('hide');
                    option.callback();
                });
            $("#alertbox-no-btn").hide();
            $("#alertbox-body").removeClass().addClass('text-' + option.color).html(option.body);
            $("#alertbox-title").removeClass().addClass('text-' + option.color).html(option.title);
            $("#alertbox").modal('show');
        }
    };
    var ConfirmBox = {
        init: function () {
            if (!isValid(this.options))
                throw new ReferenceError("参数对象异常");
        },
        show: function () {
            var option = $.extend({}, Confirmbox_Option_Default, this.options);
            $("#alertbox-yes-btn")
                .removeClass()
                .addClass('btn btn-' + option.color)
                .unbind('click')
                .click(function () {
                    $("#alertbox").modal('hide');
                    setTimeout(function () {
                        option.callback(true);
                    }, 520);
                });
            $("#alertbox-no-btn")
                .unbind('click')
                .click(function () {
                    $("#alertbox").modal('hide');
                    setTimeout(function () {
                        option.callback(false);
                    }, 520);
                })
                .show();
            $("#alertbox-body").removeClass().addClass('text-' + option.color).html(option.body);
            $("#alertbox-title").removeClass().addClass('text-' + option.color).html(option.title);
            $("#alertbox").modal('show');
        }
    };
    var Modal_Option_Default = {
        mode: 'html',                                //模态框内容（动态加载或者是预先加载好的HTML
        url: '',                                     //URL
        html: '',                                    //HTML
        title: '模态框',                              //模态框标题
        size: 'mid',                                 //模态框大小
        default_btn_color: 'primary',                //默认按钮颜色
        default_btn_title: '确定',                    //默认按钮文字
        default_btn_action: function() {             //默认按钮动作回调
            $("#generalModal").modal('hide');
        },
        loaded: function () {

        },
        close_btn_visiable: false                    //是否显示关闭按钮（右上角的默认不能没有）
    };
    var Alertbox_Option_Default = {
        body: '',          //警告框主体
        title: '提示',     //警告框标题
        color: 'primary',  //情景模式(默认default)
        callback: function(){}                    //回调
    };
    var Confirmbox_Option_Default = {
        body: '',                               //确认框主体
        title: '确认？',                       //确认框标题
        color: 'primary',                       //情景模式(默认default)
        callback: function(flag){}                    //回调，flag表示选择的行为，是为true，否为false
    };
})(window.jQuery);


