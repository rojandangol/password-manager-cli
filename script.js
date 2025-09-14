//to set master password

async function setMaster() {
    //   const account = document.getElementById("account").value;
      const master = document.getElementById("master").value;

      const res = await fetch("http://127.0.0.1:5000/set_master", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ master_password: master })
      });

      const data = await res.json();
    //   document.getElementById("output").innerText = JSON.stringify(data, null, 2);
      if(data.redirect){
        window.location.href = data.redirect;
      }else{
        alert(data.error)
      }
}


//// For Manage.html
async function addPassword() {
      const account = document.getElementById("account").value;
      const password = document.getElementById("password").value;
      const res = await fetch("/add", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ account, password })
      });
      const data = await res.json();
      alert(data.message || data.error);
    }

    async function getPassword() {
      const account = document.getElementById("getAccount").value;
      const res = await fetch(`/get/${account}`);
      const data = await res.json();
      document.getElementById("output").innerText = JSON.stringify(data, null, 2);
    }

    async function listAccounts() {
      const res = await fetch("/list");
      const data = await res.json();
      document.getElementById("listOutput").innerText = JSON.stringify(data, null, 2);
    }


    