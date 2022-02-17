import React from "react";
import {
    Box,
    Container,
    Row,
    Column,
    FooterLink,
    FooterText,
    Heading,
} from "./FooterStyles";

const Footer = () => {
    return (
        <Box>
            <h1 style={{
                // color: "green",
                textAlign: "center",
                marginTop: "-50px"
            }}>
                My Nature Watch
            </h1>
            <Container>
                <Column>
                    <Row>
                        <Heading>Project information</Heading>
                    </Row>
                    <Row>
                        <Column>
                            <FooterLink href="/api/version/date">Version date</FooterLink>
                            <FooterText id='version_date'>date</FooterText>
                        </Column>
                        <Column>
                            <FooterLink href="/api/version/redirect_to/commit_url">Commit (short) hash</FooterLink>
                            <FooterText id='version_hash'>hash</FooterText>
                        </Column>
                        <Column>
                            <FooterLink href="/api/version/redirect_to/url">Project repository</FooterLink>
                        </Column>
                    </Row>
                </Column>
                <Column>
                    <Row>
                        <Heading>Maintenance</Heading>
                    </Row>
                    <Row>
                        <Column>
                            <FooterLink href="/api/reboot">Reboot</FooterLink>
                        </Column>
                        <Column>
                            <FooterLink href="/api/shutdown">Shutdown</FooterLink>
                        </Column>
                    </Row>
                </Column>
            </Container>
        </Box>
    );
};
export default Footer;
