// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        // Complete as you see fit.
        posts: [],
        prompt: "",
        loading: false, 
        
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
    
    app.submit_post = function () {
        Vue.set(app.vue, 'loading', true); 
        console.log(app.vue.loading); 
        console.log("this is prompt: ");
        console.log(app.vue.prompt); 
        axios.post(post_url,
            {
                prompt: app.vue.prompt
            }).then(function (response) {
                console.log("done");
                app.vue.posts.push({
                    prompt: app.vue.prompt
                });
                app.enumerate(app.vue.posts);
                Vue.set(app.vue, 'prompt', ''); // Set app.vue.content to an empty string
                // Get a GET request to get the NEW PROMPT 
                axios.get(get_posts_url).then(function (response){
                    app.vue.posts = app.enumerate(response.data.posts);
                    console.log("We just got the new_prompt"); 
                    console.log(app.vue.posts); 
                    Vue.set(app.vue, 'loading', false); 
                    console.log(app.vue.loading); 
                })
        })
    };

    // This contains all the methods.
    app.methods = {
        // Complete as you see fit.
        clear_search: app.clear_search,
        submit_post: app.submit_post, 
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
        // Grabbing posts 
        Vue.set(app.vue, 'loading', false); 
        axios.get(get_posts_url).then(function (response){
            app.vue.posts = app.enumerate(response.data.posts);
            console.log("Done"); 
            console.log(app.vue.posts); 
            // for (let i = 0; i < app.vue.posts.length; i++) {
            //     console.log(app.vue.posts[i].image_data); // Print each post
            // }
        })
        
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code in it. 
init(app);
