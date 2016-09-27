Date.prototype.Format = function (fmt) { //向Date类内注册一个格式化函数，代码来源: meizz
    var o = {
        "M+": this.getMonth() + 1, //月份
        "d+": this.getDate(), //日
        "h+": this.getHours(), //小时
        "m+": this.getMinutes(), //分
        "s+": this.getSeconds(), //秒
        "q+": Math.floor((this.getMonth() + 3) / 3), //季度
        "S": this.getMilliseconds() //毫秒
    };
    if (/(y+)/.test(fmt)) fmt = fmt.replace(RegExp.$1, (this.getFullYear() + "").substr(4 - RegExp.$1.length));
    for (var k in o)
    if (new RegExp("(" + k + ")").test(fmt)) fmt = fmt.replace(RegExp.$1, (RegExp.$1.length == 1) ? (o[k]) : (("00" + o[k]).substr(("" + o[k]).length)));
    return fmt;
};
var WeJudge = {
    pager_jumper: function(url){
        var myf = '<input type="text" class="form-control" name="title" value="" placeholder="第几页？" id="pager-jumper-input"/>';
        $.ModalBox({
            'title': '跳转到',
            html: myf,
            size: 'small',
            default_btn_action: function () {
                var val = $("#pager-jumper-input").val();
                val = parseInt(val);
                if(val.toString() == "NaN" || val< 1) { val = 1; }
                location.href = url.replace('/page/1', "/page/" + val);
            }
        }).show();
    },
    problem_jumper: function(url) {
        var myf = '<input type="text" class="form-control" name="title" value="" placeholder="题目ID" id="problem-jumper-input"/>';
        $.ModalBox({
            'title': '跳转到题目',
            html: myf,
            size: 'small',
            default_btn_action: function () {
                var val = $("#problem-jumper-input").val();
                val = parseInt(val);
                if(val.toString() == "NaN" || val< 1) { val = undefined; }
                if (val != undefined) location.href = url.replace('/0', "/" + val);
            }
        }).show();
    },
    login_request_dialog: function() {
        $.ModalBox({
            title: "请登录",
            mode: 'url',
            url: '/account/login/ajax',
            default_btn_title: "登录",
            default_btn_action: function () {
                WeJudge.login_form_bind("#dialog-login-form", 'reload', true);
                $("#dialog-login-form").submit();
            }
        }).show();
    },
    login_form_bind: function (form_selector, success_action, is_modal) {
        $.ModalBox().clean_message();
        $(form_selector).submit(function(){
            $.GRestP({
                responseType: 'json',
                callback: function (flag, entity) {
                    if(flag){
                        if(success_action == "reload"){
                            location.reload();
                            return;
                        }
                        if(entity.data != null && entity.data != ""){
                            location.href = entity.data;
                        }else{
                            location.href = "/";
                        }
                    }else{
                        switch(entity.msg){
                            case -1:
                                if(is_modal){
                                    $.ModalBox().send_message("登录失败:密码错误");
                                }else{
                                    $.AlertBox({body: "密码错误", color: "warning", title: "登录失败" }).show();
                                }
                                break;
                            case -2:
                                if(is_modal){
                                     $.ModalBox().send_message("登录失败:用户名不存在");
                                }else{
                                    $.AlertBox({body: "用户名不存在", color: "warning", title: "登录失败" }).show();
                                }
                                break;
                            case -3:
                                if(is_modal){
                                    $.ModalBox().send_message("登录失败:用户名或密码为空", 'warning');
                                }else{
                                    $.AlertBox({body: "用户名或密码为空", color: "warning", title: "登录失败" }).show();
                                }
                                break;
                            case -4:
                                if(is_modal){
                                     $.ModalBox().send_message("登录失败:当前网站设置禁止用户名和密码相同的用户登录，请使用找回密码功能或者联系管理员修改密码。");
                                }else{
                                    $.AlertBox({body: "登录失败:当前网站设置禁止用户名和密码相同的用户登录，请使用找回密码功能或者联系管理员修改密码。", color: "warning", title: "登录失败" }).show();
                                }
                                break;
                            case -5:
                                if(is_modal){
                                     $.ModalBox().send_message("登录失败:当前账号处于禁止登录状态，请与管理员联系。");
                                }else{
                                    $.AlertBox({body: "登录失败:前账号处于禁止登录状态，请与管理员联系", color: "warning", title: "登录失败" }).show();
                                }
                                break;
                            case -6:
                                if(is_modal){
                                     $.ModalBox().send_message("登录失败:由于网站全局设置，您的账号暂时不能登录。");
                                }else{
                                    $.AlertBox({body: "登录失败：由于网站全局设置，您的账号暂时不能登录。", color: "warning", title: "登录失败" }).show();
                                }
                                break;
                            default:
                                if(is_modal){
                                     $.ModalBox().send_message("重试密码次数过多,请"+ entity.msg +"秒后再试。");
                                }else{
                                    $.AlertBox({body: "重试密码次数过多,请"+ entity.msg +"秒后再试。", color: "warning", title: "登录失败" }).show();
                                }

                        }
                    }
                }
            }).submit_form(this);
            return false;
        });
    },
    set_countdown_timer: function (sec, container) {
        WeJudge.countdown_time_tick(sec, container);
    },
    countdown_time_tick: function(intDiff, container){
        var day=0,
            hour=0,
            minute=0,
            second=0;//时间默认值

        if(intDiff > 0){
            day = Math.floor(intDiff / (60 * 60 * 24));
            hour = Math.floor(intDiff / (60 * 60)) - (day * 24);
            minute = Math.floor(intDiff / 60) - (day * 24 * 60) - (hour * 60);
            second = Math.floor(intDiff) - (day * 24 * 60 * 60) - (hour * 60 * 60) - (minute * 60);
        }
        if (minute <= 9) minute = '0' + minute;
        if (second <= 9) second = '0' + second;
        if (day != 0)
        {
            $(container).html(day + "天" + hour+'时' + minute+'分' + second+'秒');
        }
        else{
            $(container).html(hour+'时' + minute+'分' + second+'秒');
        }
        intDiff--;
        if (intDiff < 0){
            return false;
        }else{
            setTimeout("WeJudge.countdown_time_tick("+intDiff+", \""+container+"\")", 1000);
        }
    },
    set_normal_timer: function (sec, container) {
        WeJudge.normal_timer(sec, container);
    },
    normal_timer: function (sec, container) {
        $(container).html(new Date(sec * 1000).Format("yyyy-MM-dd hh:mm:ss"));
        setTimeout("WeJudge.normal_timer("+(sec+1)+", \""+container+"\")", 1000);
    }
};
