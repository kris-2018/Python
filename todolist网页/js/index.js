

var todoc = 0;
var donec = 0;

var todolist = document.getElementById('todolist');
var donelist = document.getElementById('donelist');

var todocount = document.getElementById('todocount');
var donecount = document.getElementById('donecount');


//添加ToDo
function postaction() {
    var title = document.getElementById('title');
    if (title.value === ""){
        alert('内容不能为空！')
    }else {
        var li = document.createElement('li');
        li.innerHTML = '<input type="checkbox" onchange="update();"> ' +
            '<input class="title" type="text" onchange="change();" onclick="edit();">' +
            '<a href="javascript:remove();">-</a> ';
        if (todoc == 0){   //第一次添加元素appendChild
            todolist.appendChild(li);
        }else {
            todolist.insertBefore(li,todolist.children[0]);
        }
        var testTitle = document.getElementsByClassName('title')[0];
        testTitle.value = title.value;

        loop('todolist');
        todoc ++;
        todocount.innerText = todoc;

        title.value = "";
    }
}

//循环，每次添加不同的i值
function loop(str) {
    var list = null;
    str === 'todolist' ? list = todolist : list = donelist;
    childs = list.childNodes;
    for (var i = 0; i < childs.length;i++){
        childs[i].children[0].setAttribute('onchange','update("'+i+'", "'+str+'")');
        childs[i].children[1].setAttribute('onclick','edit("'+i+'", "'+str+'")');
        childs[i].children[1].setAttribute('onchange','change("'+i+'", "'+str+'","'+childs[i].children[1].value+'")');
        childs[i].children[2].setAttribute('href','javascript:remove("'+i+'", "'+str+'")');
    }
}

//update方法
function update(n,str) {
    var list = null;
    str === 'todolist' ? list = todolist : list = donelist;

    var li = null;
    childs = list.childNodes;
    for (var i = 0; i < childs.length; i++){
        if (i === Number(n)){
            li = childs[i]
        }
    }
    remove(n,str); //删除原有的，得到li并刷新原有的li

    if (str ==='todolist'){
        if (donec === 0){
            donelist.appendChild(li);
        }else {
            donelist.insertBefore(li,donelist.children[0]);
        }
        loop('donelist');
        donec++;
        donecount.innerText = donec;
    }else if (str === 'donelist'){
        todolist.appendChild(li);
        loop('todolist')
        todoc++;
        todocount.innerText = todoc;
    }
}

//edit 方法 编辑title
function edit(n,str) {
    var list = null;
    str === 'todolist' ? list = todolist : list = donelist;
    childs = list.childNodes;
    for (var i = 0; i < childs.length;i++){
        if (i === Number(n)){
            childs[i].children[1].style.border = '1px solid #ccc';
        }
    }
}

// change方法 失去焦点
function change(n,str,oldValue) {
    var list = null;
    str === 'todolist' ? list = todolist : list = donelist;
    childs = list.childNodes;
    for (var i = 0; i < childs.length; i++){
        if (i === Number(n)){
            childs[i].children[1].style.border = 'none';
            if (childs[i].children[1].value === ""){
                alert('内容不能为空');
                childs[i].children[1].value = oldValue;
            }
        }
    }
    loop(str);
}
//清除列表清单
function remove(n,str) {
    var list = null;
    if (str === 'todolist'){
        list = todolist;
        todoc--;
        todocount.innerText = todoc;
    }else if (str === 'donelist'){
        list = donelist;
        donec--;
        donecount.innerText =donec;
    }
    childs = list.childNodes;
    for (var i = childs.length-1;i >= 0;i--){
        if (i === Number(n)){
            list.removeChild(childs[n]);
        }
    }
    loop(str);
}
//清除所有列表

function clear() {
    childs1 = todolist.childNodes;
    for (var i = childs1.length-1; i >= 0 ; i--){
        todolist.removeChild(childs1[i]);
    }
    childs2 = donelist.childNodes;
    for (var j = childs2.length-1 ; j >= 0; j--){
        donelist.removeChild(childs2[j]);
    }
    todoc = 0;
    donec = 0;
    todocount.innerText = todoc;
    donecount.innerText = donec;
}
