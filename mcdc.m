function [ new_recommendation_set] = mcdc( Ri, S, k)
%MCDC Minimum Conductance Dissimilarity Cut
%Params: Ri- N x 1 matrix with scores for each item using the base
%recommender algorithm.
%S: N X N similarity matrix for each item, assumed to be sparse
%k: the number of items to recommend

N = size(S);
W = zeros(N,N);
for i=1:1:N
    for j=1:1:N
        W(i,j) = (1-S(i,j))*(Ri(i)+Ri(j));
    end
end

normalizedW = sum(W);
W = W ./ repmat(normalizedW',1,N);
D = W;
[V L] = eigs(D);
recs = V(:,2);
[v i] =sort(recs);
new_recommendation_set = i(end-k:end);

end

