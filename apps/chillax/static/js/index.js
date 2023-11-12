// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        // Complete as you see fit.
        rows: [],
        meows: [],
       
    };    
    
    app.enumerate = (a) => {
        // This adds an _idx field to each element of the array.
        let k = 0;
        a.map((e) => {e._idx = k++;});
        return a;
    };    

    app.clear_search = function () {
        app.vue.search_filter = "";
    };
    
    app.add_meow = function (m) {
        if (m.author != undefined){
            console.log("m exists");
            newContent = "RT " + m.author + ": " + m.content; 
            axios.post(meow_url,
                {
                    user_name: app.vue.rows[app.vue.currentID].username,
                    content: newContent,
                }).then(function (response) {
                    // app.vue.rows[row_idx].currentID = app.vue.currentID; 
                    console.log("done");
                    app.vue.meows.push({
                        author: app.vue.rows[app.vue.currentID].username,
                        content: newContent,
                        timestamp: response.data.ts, 
                        total_replies: parseInt("0"),
                    });
                    app.enumerate(app.vue.meows);
                    app.assignMeows();
                    Vue.set(app.vue, 'content', ''); // Set app.vue.content to an empty string
            })
        }
        else{
            console.log("m does not exist");
            if (app.vue.reply_status == true){ // we are replying 
                console.log("reply is true");
                // let m = app.vue.meows[m._idx];
                
                let first_m = app.vue.meows[app.vue.reply_index]; 
                let new_m = {};
                new_m.currentID = first_m.currentID;  
                new_m.author = first_m.author; 
                new_m.content = first_m.content; 
                new_m.timestamp = first_m.timestamp; 
                new_m.reply_owner = first_m.reply_owner; 
                new_m.total_replies = parseInt(first_m.total_replies) + 1; 
                new_m._idx = first_m._idx; 
                Vue.set(app.vue.meows, new_m._idx, new_m); 
                console.log(app.vue.meows[new_m._idx]);
                
            }
            else{ // if we are not replying 
                axios.post(meow_url,
                    {
                        user_name: app.vue.rows[app.vue.currentID].username,
                        content: app.vue.content,
                    }).then(function (response) {
                        // app.vue.rows[row_idx].currentID = app.vue.currentID; 
                        console.log("done");
                        app.vue.meows.push({
                            author: app.vue.rows[app.vue.currentID].username,
                            content: app.vue.content,
                            timestamp: response.data.ts, 
                            total_replies: parseInt("0"),
                        });
                        app.enumerate(app.vue.meows);
                        app.assignMeows();
                        Vue.set(app.vue, 'content', ''); // Set app.vue.content to an empty string
                })
            }
        }
    };

    // This contains all the methods.
    app.methods = {
        // Complete as you see fit.
        clear_search: app.clear_search,
        add_meow: app.add_meow, 
    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    // And this initializes it.
    app.init = () => {
        // Put here any initialization code.
        axios.get(get_users_url).then(function (response){
            app.vue.rows = app.enumerate(response.data.rows);
            app.vue.meows = app.enumerate(response.data.meows);
            app.vue.current = response.data.current; 
            app.vue.currentUser = response.data.currentUser; 
            // followList gurantees we get users followed by current user 
            app.vue.followList = app.enumerate(response.data.followList);  
            // Rows is now just all the auth users in database 
            for (let r of app.vue.rows) {
                if (app.vue.current === r.email) {
                    app.vue.currentID = r._idx; // FINDING THE OWNERS INDEX 
                    r.currentID = r._idx; 
                }
            }
            console.log("owner index ");
            console.log(app.vue.currentID);
            //adding those in the following database to the rows. 
            for (let i of app.vue.followList) {
                const existsInRows = app.vue.rows.some((row) => row.username === i.user_name);
                const existingRow = app.vue.rows.find((row) => row.username === i.user_name);
                if (!existsInRows) {
                    // console.log("adding");
                    // console.log(i.user_name);
                  app.vue.rows.push({
                    username: i.user_name,
                    currentID: app.vue.currentID,
                  });
                }
                else{
                    existingRow.currentID = app.vue.currentID;
                }
            }
            for(let i of app.vue.meows){ // every meow intitally gets zero 
                let new_m = {}; // updating count of owner 
                new_m.currentID = i.currentID;  
                new_m.author = i.author; 
                new_m.content = i.content; 
                new_m.timestamp = i.timestamp; 
                new_m.reply_owner = i.reply_owner; 
                new_m.total_replies = parseInt("0") ; 
                new_m._idx = i._idx; 
                Vue.set(app.vue.meows, new_m._idx, new_m);
            }
            
            // counting replies 
            for(let i of app.vue.meows){
                if (parseInt(i.reply_owner) >= 0 ){ // meow has an owner 
                    // find owner of 
                    let currentOwner = app.vue.meows[i.reply_owner];
                    let new_m = {}; // updating count of owner 
                    new_m.currentID = currentOwner.currentID;  
                    new_m.author = currentOwner.author; 
                    new_m.content = currentOwner.content; 
                    new_m.timestamp = currentOwner.timestamp; 
                    new_m.reply_owner = currentOwner.reply_owner; 
                    new_m.total_replies =  parseInt(currentOwner.total_replies) + 1; 
                    new_m._idx = currentOwner._idx; 
                    Vue.set(app.vue.meows, new_m._idx, new_m);
                }
            }
            // for(let i of app.vue.meows){
            //     if(parseInt(i.total_replies) >= 0){
            //         console.log(i); 
            //     }
            // }
            app.vue.rows = app.enumerate(response.data.rows); // enumerate rows
            console.log("FIRST");
            // console.log(app.vue.rows);
            // console.log(app.vue.followList);
            app.assignMeows();
        })
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code in it. 
init(app);
