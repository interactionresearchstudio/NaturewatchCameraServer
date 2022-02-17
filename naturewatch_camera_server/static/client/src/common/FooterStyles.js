import styled from 'styled-components';

export const Box = styled.footer `
padding: 80px 60px;
background: black;
position: relative;
width: 100%;
left:0;
bottom:0;
right:0;


@media (max-width: 1000px) {
	padding: 70px 30px;
}
`;

export const Container = styled.div `
	display: flex;
	flex-direction: column;
	justify-content: center;
	max-width: 1000px;
	margin: 0 auto;
	/* background: red; */
`

export const Column = styled.div `
display: flex;
flex-direction: column;
text-align: left;
margin-left: 60px;
`;

export const Row = styled.div `
display: grid;
grid-template-columns: repeat(auto-fill,
						minmax(185px, 1fr));
grid-gap: 20px;

@media (max-width: 1000px) {
	grid-template-columns: repeat(auto-fill,
						minmax(200px, 1fr));
}
`;

export const FooterLink = styled.a `
color: #fff;
margin-bottom: 20px;
font-size: 18px;
text-decoration: none;

&:hover {
	color: green;
	transition: 200ms ease-in;
}
`;

export const FooterText = styled.p `
color: #9ca2a6;
margin-bottom: 10px;
font-size: 15px;
text-decoration: none;
`;

export const Heading = styled.p `
font-size: 24px;
color: #fff;
margin-bottom: 40px;
font-weight: bold;
`;
