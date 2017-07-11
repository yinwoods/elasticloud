function getCookie(name) {
    var nameEQ = name + "=";
    var ca = document.cookie.split(';');
    for(var i=0;i < ca.length;i++) {
        var c = ca[i];
        while (c.charAt(0)==' ') c = c.substring(1,c.length);
        if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
    }
    return null;
}

function remove_job(job_id, job_name) {
  if(confirm("删除任务: " + job_name + "?")) {
    $.ajax({
      type: 'DELETE',
      url: '/web/job/remove/',
      data: 'job_id=' + job_id,
      beforeSend: function(xhr) {
        xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
        window.console.log(getCookie('csrftoken'));
      },
      success: function(message) {
        if(message == 'true') {
          window.location.hash = 'true';
          window.location.reload();
        }
      },
      error: function(message) {
        if(message == 'false') {
            window.location.hash = 'false';
            window.location.reload();
        }
      }
    })
  }
}

function launch_job(job_id, job_name) {
  if(confirm("启动任务: " + job_name + "?")) {
    $.ajax({
      type: 'POST',
      url: '/web/job/launch/',
      data: 'job_id=' + job_id,
      success: function(message) {
        alert(message);
        window.location.reload();
      },
      error: function(message) {
        alert("Error! Please check your docker proxy server.");
      }
    })
  }
}

function remove_compute(container_id, master_ip) {
  if(confirm("删除计算集群: " + master_ip + "?")) {
    $.ajax({
      type: 'DELETE',
      url: '/web/cluster/compute/remove/',
      data: 'container_id=' + container_id,
      success: function(message) {
        if(message == 'true') {
          window.location.hash = 'true';
          window.location.reload();
        }
      },
      error: function(message) {
        if(message == 'false') {
            window.location.hash = 'false';
            window.location.reload();
        }
      }
    })
  }
}

function remove_storage(master_ip) {
  if(confirm("删除存储集群: " + master_ip + "?")) {
    $.ajax({
      type: 'GET',
      url: '/web/cluster/storage/remove/',
      data: 'master_ip=' + master_ip,
      success: function(message) {
        if(message == 'true') {
          window.location.hash = 'true';
          window.location.reload();
        }
      },
      error: function(message) {
        if(message == 'false') {
            window.location.hash = 'false';
            window.location.reload();
        }
      }
    })
  }
}

function fake_load() {
    var cur_value = 1,
        progress;

    // Make a loader.
    var loader = new PNotify({
        title: "准备创建集群...",
        text: '<div class="progress progress-striped active" style="margin:0">\
  <div class="progress-bar" role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100" style="width: 0">\
    <span class="sr-only">0%</span>\
  </div>\
</div>',
        //icon: 'fa fa-moon-o fa-spin',
        icon: 'fa fa-cog fa-spin',
        hide: false,
        buttons: {
            closer: true,
            sticker: true,
        },
        type: 'info',
        styling: 'bootstrap3',
        addclass: 'dark',
        history: {
            history: false
        },
        before_init: function(notice) {
            $("form").submit();
        },
        before_open: function(notice) {
            progress = notice.get().find("div.progress-bar");
            progress.width(cur_value + "%").attr("aria-valuenow", cur_value).find("span").html(cur_value + "%");
            // Pretend to do something.
            var timer = setInterval(function() {
                if (cur_value >= 30 && cur_value < 50) {
                    loader.update({
                        title: "正在读取集群镜像...",
                        icon: "fa fa-circle-o-notch fa-spin"
                    });
                }
                if (cur_value >= 50 && cur_value < 80) {
                    loader.update({
                        title: "正在连接镜像...",
                        icon: "fa fa-refresh fa-spin"
                    });
                }
                if (cur_value >= 80 && cur_value < 100) {
                    loader.update({
                        title: "即将完成！",
                        icon: "fa fa-spinner fa-spin"
                    });
                }
                if (cur_value >= 100) {
                    // Remove the interval.
                    window.clearInterval(timer);
                    loader.remove();
                    return;
                }
                cur_value += 1;
                progress.width(cur_value + "%").attr("aria-valuenow", cur_value).find("span").html(cur_value + "%");
            }, 65);
        },
    });
}
