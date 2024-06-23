-- users
INSERT INTO public.users VALUES ('mary', 'afsfsa', '', NULL);
INSERT INTO public.users VALUES ('joe', 'afsfsa', '', NULL);
INSERT INTO public.users VALUES ('anon', 'afsfsa', '', NULL);
INSERT INTO public.users VALUES ('atka', 'atka', '', NULL);

-- posts
INSERT INTO public.posts VALUES (1, 'Me at the zoo', 'https://bmeme-images.s3.eu-north-1.amazonaws.com/011d1f9d-6687-40c9-9bca-501e11acd096', 1719156700, 'joe', NULL);
INSERT INTO public.posts VALUES (3, 'This is a good meme', 'https://bmeme-images.s3.eu-north-1.amazonaws.com/011d1f9d-6687-40c9-9bca-501e11acd096', 1719156705, 'atka', NULL);
INSERT INTO public.posts VALUES (4, 'No, I am better', 'https://bmeme-images.s3.eu-north-1.amazonaws.com/d1457afb-3b4e-43d7-94ad-9892b737cb44', 1719156767, 'mary', NULL);

-- votes
INSERT INTO public.votes VALUES (1, 'anon', 1);
INSERT INTO public.votes VALUES (1, 'atka', -1);
INSERT INTO public.votes VALUES (3, 'atka', 1);
INSERT INTO public.votes VALUES (4, 'atka', -1);
INSERT INTO public.votes VALUES (4, 'anon', -1);
INSERT INTO public.votes VALUES (3, 'joe', 1);
INSERT INTO public.votes VALUES (4, 'mary', 1);